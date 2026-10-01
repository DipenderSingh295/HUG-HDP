from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log, pi, sqrt
from typing import Callable, Iterable, Optional, Sequence
import warnings

import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.optimize import minimize
from scipy.special import expit, logsumexp
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors


Array = np.ndarray
PairwiseHDPScorer = Callable[[Array, Array, Array], Optional[Array]]


@dataclass(frozen=True)
class SourceProject:
    key: str
    family: str
    X: Array
    y: Array


@dataclass(frozen=True)
class TargetProject:
    key: str
    family: str
    X: Array


@dataclass
class EvidenceContext:
    p_h: Array
    p_u: Array
    c: Array
    z: Array
    contributing_families: tuple[str, ...]
    candidate_families: tuple[str, ...]


@dataclass
class Episode:
    c: Array
    z: Array
    y: Array


@dataclass
class EnvironmentResult:
    omitted_family: str
    probability: Array
    conditional_risk: Array
    transfer_utility: Array
    gate: Array
    p_h: Array
    p_u: Array
    coverage: float
    contributing_families: tuple[str, ...]
    candidate_families: tuple[str, ...]


@dataclass
class HUGResult:
    probability: Array
    environments: tuple[EnvironmentResult, ...]


class _LogisticCalibrator:
    def __init__(self, c_grid: Sequence[float], max_iter: int):
        self.c_grid = tuple(float(c) for c in c_grid)
        self.max_iter = int(max_iter)
        self.model: Optional[LogisticRegression] = None
        self.constant: Optional[float] = None
        self.selected_c: Optional[float] = None

    @staticmethod
    def _weights(groups: Array) -> Array:
        groups = np.asarray(groups)
        unique, counts = np.unique(groups, return_counts=True)
        count_map = {g: c for g, c in zip(unique, counts)}
        w = np.array([1.0 / count_map[g] for g in groups], dtype=float)
        return w * (len(w) / np.sum(w))

    def _fit_one(self, x: Array, y: Array, groups: Array, c: float):
        if np.unique(y).size < 2:
            return float(np.average(y, weights=self._weights(groups)))
        model = LogisticRegression(C=float(c), solver="lbfgs", max_iter=self.max_iter)
        model.fit(x.reshape(-1, 1), y, sample_weight=self._weights(groups))
        return model

    @staticmethod
    def _predict_one(model, x: Array) -> Array:
        if isinstance(model, float):
            return np.full(len(x), model, dtype=float)
        return model.predict_proba(x.reshape(-1, 1))[:, 1]

    def fit(self, x: Array, y: Array, groups: Array) -> "_LogisticCalibrator":
        x = np.asarray(x, dtype=float).reshape(-1)
        y = np.asarray(y, dtype=int).reshape(-1)
        groups = np.asarray(groups)
        valid = np.isfinite(x) & np.isfinite(y.astype(float))
        x, y, groups = x[valid], y[valid], groups[valid]
        if len(x) == 0:
            raise RuntimeError("No calibration observations are available.")
        unique_groups = np.unique(groups)
        if np.unique(y).size < 2:
            self.constant = float(np.average(y, weights=self._weights(groups)))
            self.selected_c = self.c_grid[0]
            return self
        if unique_groups.size < 2:
            best_c = self.c_grid[0]
        else:
            best_c = None
            best_loss = np.inf
            for c in self.c_grid:
                losses = []
                for g in unique_groups:
                    train = groups != g
                    test = groups == g
                    if not np.any(train) or not np.any(test):
                        continue
                    fitted = self._fit_one(x[train], y[train], groups[train], c)
                    pred = self._predict_one(fitted, x[test])
                    losses.append(float(np.mean((y[test] - pred) ** 2)))
                if losses:
                    loss = float(np.mean(losses))
                    if loss < best_loss:
                        best_loss = loss
                        best_c = c
            if best_c is None:
                best_c = self.c_grid[0]
        self.selected_c = float(best_c)
        fitted = self._fit_one(x, y, groups, self.selected_c)
        if isinstance(fitted, float):
            self.constant = fitted
        else:
            self.model = fitted
        return self

    def predict(self, x: Array) -> Array:
        x = np.asarray(x, dtype=float).reshape(-1)
        if self.constant is not None:
            return np.full(len(x), self.constant, dtype=float)
        if self.model is None:
            raise RuntimeError("Calibrator is not fitted.")
        return self.model.predict_proba(x.reshape(-1, 1))[:, 1]


class _HierarchicalRiskModel:
    def __init__(
        self,
        quadrature_orders: Sequence[int],
        quadrature_tol: float,
        max_iter: int,
    ):
        self.quadrature_orders = tuple(int(x) for x in quadrature_orders)
        self.quadrature_tol = float(quadrature_tol)
        self.max_iter = int(max_iter)
        self.theta: Optional[Array] = None
        self.order: Optional[int] = None
        self.project_dim = 5
        self.local_dim = 5

    def _objective_gradient(self, theta: Array, episodes: Sequence[Episode], order: int):
        beta0 = theta[0]
        beta_p = theta[1:1 + self.project_dim]
        beta_l = theta[1 + self.project_dim:1 + self.project_dim + self.local_dim]
        log_sigma = theta[-1]
        sigma = np.exp(log_sigma)
        nodes, weights = hermgauss(order)
        log_weights = np.log(weights) - 0.5 * np.log(pi)
        total_ll = 0.0
        total_grad = np.zeros_like(theta)
        for episode in episodes:
            c = np.asarray(episode.c, dtype=float)
            z = np.asarray(episode.z, dtype=float)
            y = np.asarray(episode.y, dtype=float)
            centered = z - np.mean(z, axis=0, keepdims=True)
            local = centered @ beta_l
            mu = beta0 + c @ beta_p
            log_terms = np.empty(order, dtype=float)
            gradients = np.empty((order, len(theta)), dtype=float)
            for j, node in enumerate(nodes):
                shift = sqrt(2.0) * sigma * node
                eta = mu + shift + local
                p = expit(eta)
                ll = np.sum(y * eta - np.logaddexp(0.0, eta))
                residual = y - p
                residual_sum = float(np.sum(residual))
                g = np.zeros_like(theta)
                g[0] = residual_sum
                g[1:1 + self.project_dim] = c * residual_sum
                g[1 + self.project_dim:1 + self.project_dim + self.local_dim] = centered.T @ residual
                g[-1] = shift * residual_sum
                log_terms[j] = log_weights[j] + ll
                gradients[j] = g
            marginal = logsumexp(log_terms)
            posterior = np.exp(log_terms - marginal)
            total_ll += marginal
            total_grad += posterior @ gradients
        return -total_ll, -total_grad

    def fit(self, episodes: Sequence[Episode]) -> "_HierarchicalRiskModel":
        if not episodes:
            raise RuntimeError("No pseudo-target episodes are available.")
        prevalence = np.concatenate([np.asarray(e.y, dtype=float) for e in episodes]).mean()
        prevalence = float(np.clip(prevalence, 1e-6, 1.0 - 1e-6))
        beta0 = np.log(prevalence / (1.0 - prevalence))
        theta = np.zeros(1 + self.project_dim + self.local_dim + 1, dtype=float)
        theta[0] = beta0
        theta[-1] = np.log(0.5)
        bounds = [(None, None)] * (len(theta) - 1) + [(-8.0, 3.0)]
        previous_ll = None
        last_finite = None
        for order in self.quadrature_orders:
            result = minimize(
                lambda t: self._objective_gradient(t, episodes, order),
                theta,
                method="L-BFGS-B",
                jac=True,
                bounds=bounds,
                options={"maxiter": self.max_iter, "ftol": 1e-10, "gtol": 1e-7},
            )
            if not np.isfinite(result.fun) or not np.all(np.isfinite(result.x)):
                continue
            theta = result.x
            ll = -float(result.fun)
            last_finite = (theta.copy(), int(order), ll)
            if previous_ll is not None:
                scale = max(1.0, abs(previous_ll))
                if abs(ll - previous_ll) <= self.quadrature_tol * scale:
                    self.theta = theta.copy()
                    self.order = int(order)
                    return self
            previous_ll = ll
        if last_finite is None:
            raise RuntimeError("Hierarchical risk model failed to obtain a finite solution.")
        self.theta = last_finite[0]
        self.order = last_finite[1]
        warnings.warn("Gauss-Hermite quadrature did not reach the requested stability; using the highest finite optimized resolution.", RuntimeWarning)
        return self

    def predict(self, c: Array, z: Array) -> Array:
        if self.theta is None or self.order is None:
            raise RuntimeError("Hierarchical risk model is not fitted.")
        theta = self.theta
        beta0 = theta[0]
        beta_p = theta[1:1 + self.project_dim]
        beta_l = theta[1 + self.project_dim:1 + self.project_dim + self.local_dim]
        sigma = np.exp(theta[-1])
        z = np.asarray(z, dtype=float)
        centered = z - np.mean(z, axis=0, keepdims=True)
        local = centered @ beta_l
        mu = beta0 + np.asarray(c, dtype=float) @ beta_p
        nodes, weights = hermgauss(self.order)
        q = np.zeros(len(z), dtype=float)
        for node, weight in zip(nodes, weights):
            alpha = mu + sqrt(2.0) * sigma * node
            q += (weight / sqrt(pi)) * expit(alpha + local)
        return np.clip(q, 0.0, 1.0)


class HUGHDP:
    def __init__(
        self,
        hdp_pair_scorer: PairwiseHDPScorer,
        overlap_pairs: Optional[Iterable[tuple[str, str]]] = None,
        calibration_c_grid: Sequence[float] = (0.01, 0.1, 1.0, 10.0, 100.0),
        calibration_max_iter: int = 2000,
        quadrature_orders: Sequence[int] = (10, 20, 30, 40, 60),
        quadrature_tol: float = 1e-6,
        hierarchical_max_iter: int = 500,
        epsilon: float = 1e-8,
    ):
        self.hdp_pair_scorer = hdp_pair_scorer
        self.overlap_pairs = {
            frozenset((str(a), str(b))) for a, b in (overlap_pairs or [])
        }
        self.calibration_c_grid = tuple(calibration_c_grid)
        self.calibration_max_iter = int(calibration_max_iter)
        self.quadrature_orders = tuple(quadrature_orders)
        self.quadrature_tol = float(quadrature_tol)
        self.hierarchical_max_iter = int(hierarchical_max_iter)
        self.epsilon = float(epsilon)

    def _overlap(self, a: str, b: str) -> bool:
        return frozenset((str(a), str(b))) in self.overlap_pairs

    def _validate_source(self, p: SourceProject) -> SourceProject:
        X = np.asarray(p.X, dtype=float)
        y = np.asarray(p.y, dtype=int).reshape(-1)
        if X.ndim != 2 or len(X) != len(y):
            raise ValueError(f"Invalid source project: {p.key}")
        if np.setdiff1d(np.unique(y), np.array([0, 1])).size:
            raise ValueError(f"Labels must be binary for project: {p.key}")
        return SourceProject(str(p.key), str(p.family), X, y)

    def _validate_target(self, p: TargetProject) -> TargetProject:
        X = np.asarray(p.X, dtype=float)
        if X.ndim != 2:
            raise ValueError(f"Invalid target project: {p.key}")
        return TargetProject(str(p.key), str(p.family), X)

    def _source_pool_for(self, sources: Sequence[SourceProject], target_key: str, target_family: str):
        return [
            s for s in sources
            if s.family != target_family and not self._overlap(s.key, target_key)
        ]

    def _aggregate_raw_hdp(self, sources: Sequence[SourceProject], target: TargetProject):
        by_family: dict[str, list[Array]] = {}
        for source in sources:
            score = self.hdp_pair_scorer(source.X, source.y, target.X)
            if score is None:
                continue
            score = np.asarray(score, dtype=float).reshape(-1)
            if len(score) != len(target.X) or not np.all(np.isfinite(score)):
                continue
            by_family.setdefault(source.family, []).append(score)
        if not by_family:
            return None, tuple()
        family_scores = []
        contributing = []
        for family in sorted(by_family):
            values = by_family[family]
            if not values:
                continue
            family_scores.append(np.mean(np.vstack(values), axis=0))
            contributing.append(family)
        if not family_scores:
            return None, tuple()
        return np.mean(np.vstack(family_scores), axis=0), tuple(contributing)

    def _structural_score(self, X: Array) -> Array:
        X = np.asarray(X, dtype=float)
        X = np.where(np.isfinite(X), X, np.nan)
        med = np.nanmedian(X, axis=0)
        med = np.where(np.isfinite(med), med, 0.0)
        X_imp = np.where(np.isnan(X), med, X)
        return np.mean(X_imp > med, axis=1).astype(float)

    def _fit_h_calibrator(self, sources: Sequence[SourceProject]) -> _LogisticCalibrator:
        scores = []
        labels = []
        groups = []
        for project in sources:
            train = self._source_pool_for(sources, project.key, project.family)
            if not train:
                continue
            raw, _ = self._aggregate_raw_hdp(
                train,
                TargetProject(project.key, project.family, project.X),
            )
            if raw is None:
                continue
            scores.append(raw)
            labels.append(project.y)
            groups.append(np.full(len(project.y), project.key, dtype=object))
        if not scores:
            raise RuntimeError("Heterogeneous-transfer calibration is infeasible.")
        calibrator = _LogisticCalibrator(self.calibration_c_grid, self.calibration_max_iter)
        calibrator.fit(np.concatenate(scores), np.concatenate(labels), np.concatenate(groups))
        return calibrator

    def _fit_u_calibrator(self, sources: Sequence[SourceProject]) -> _LogisticCalibrator:
        scores = []
        labels = []
        groups = []
        for project in sources:
            score = self._structural_score(project.X)
            scores.append(score)
            labels.append(project.y)
            groups.append(np.full(len(project.y), project.key, dtype=object))
        if not scores:
            raise RuntimeError("Target-structural calibration is infeasible.")
        calibrator = _LogisticCalibrator(self.calibration_c_grid, self.calibration_max_iter)
        calibrator.fit(np.concatenate(scores), np.concatenate(labels), np.concatenate(groups))
        return calibrator

    def _phi(self, X: Array) -> Array:
        X = np.asarray(X, dtype=float)
        X = np.where(np.isfinite(X), X, np.nan)
        med = np.nanmedian(X, axis=0)
        med = np.where(np.isfinite(med), med, 0.0)
        X = np.where(np.isnan(X), med, X)
        X = np.sign(X) * np.log1p(np.abs(X))
        center = np.median(X, axis=0)
        q25 = np.quantile(X, 0.25, axis=0)
        q75 = np.quantile(X, 0.75, axis=0)
        scale = np.maximum(q75 - q25, self.epsilon)
        Z = (X - center) / scale
        return np.column_stack(
            [
                np.mean(Z, axis=1),
                np.std(Z, axis=1),
                np.min(Z, axis=1),
                np.max(Z, axis=1),
                np.median(Z, axis=1),
                np.mean(np.abs(Z), axis=1),
                np.quantile(Z, 0.25, axis=1),
                np.quantile(Z, 0.75, axis=1),
            ]
        )

    def _context(self, sources: Sequence[SourceProject], target: TargetProject, p_h: Array, p_u: Array):
        source_phi = np.vstack([self._phi(s.X) for s in sources])
        target_phi = self._phi(target.X)
        mean = np.mean(source_phi, axis=0)
        sd = np.std(source_phi, axis=0)
        sd = np.maximum(sd, self.epsilon)
        source_phi = (source_phi - mean) / sd
        target_phi = (target_phi - mean) / sd
        n_source = len(source_phi)
        if n_source < 2:
            raise RuntimeError("Insufficient source support observations.")
        k = max(1, ceil(log(n_source)))
        k_source = min(k, n_source - 1)
        source_nn = NearestNeighbors(n_neighbors=k_source + 1).fit(source_phi)
        source_dist = source_nn.kneighbors(source_phi, return_distance=True)[0][:, 1:]
        source_raw = np.mean(source_dist, axis=1)
        k_target = min(k, n_source)
        target_nn = NearestNeighbors(n_neighbors=k_target).fit(source_phi)
        target_dist = target_nn.kneighbors(target_phi, return_distance=True)[0]
        target_raw = np.mean(target_dist, axis=1)
        support_median = np.median(source_raw)
        support_mad = np.median(np.abs(source_raw - support_median))
        support_mad = max(float(support_mad), self.epsilon)
        d_s = (target_raw - support_median) / support_mad
        d_phi = source_phi.shape[1]
        d_mu = np.linalg.norm(np.mean(source_phi, axis=0) - np.mean(target_phi, axis=0)) / sqrt(d_phi)
        source_cov = self._covariance(source_phi)
        target_cov = self._covariance(target_phi)
        d_sigma = np.linalg.norm(source_cov - target_cov, ord="fro") / d_phi
        d_h = np.abs(p_h - p_u)
        ph = np.clip(p_h, self.epsilon, 1.0 - self.epsilon)
        h_h = -ph * np.log(ph) - (1.0 - ph) * np.log(1.0 - ph)
        z = np.column_stack([p_h, p_u, d_h, d_s, h_h])
        mean_m = float(np.mean(0.5 * (p_h + p_u)))
        c = np.array(
            [
                float(d_mu),
                float(d_sigma),
                float(np.mean(d_s)),
                float(np.mean(d_h)),
                mean_m,
            ],
            dtype=float,
        )
        return c, z

    def _covariance(self, X: Array) -> Array:
        X = np.asarray(X, dtype=float)
        d = X.shape[1]
        if len(X) <= 1:
            cov = np.zeros((d, d), dtype=float)
        else:
            cov = np.asarray(np.cov(X, rowvar=False), dtype=float)
            if cov.ndim == 0:
                cov = np.array([[float(cov)]], dtype=float)
        return cov + self.epsilon * np.eye(d)

    def _evidence_context(self, sources: Sequence[SourceProject], target: TargetProject):
        candidate_families = tuple(sorted({s.family for s in sources}))
        if not candidate_families:
            return None
        raw_h, contributing = self._aggregate_raw_hdp(sources, target)
        if raw_h is None or not contributing:
            return None
        h_calibrator = self._fit_h_calibrator(sources)
        u_calibrator = self._fit_u_calibrator(sources)
        p_h = np.clip(h_calibrator.predict(raw_h), 0.0, 1.0)
        p_u = np.clip(u_calibrator.predict(self._structural_score(target.X)), 0.0, 1.0)
        c, z = self._context(sources, target, p_h, p_u)
        return EvidenceContext(p_h, p_u, c, z, contributing, candidate_families)

    def _episodes(self, environment_sources: Sequence[SourceProject]):
        episodes = []
        for q in environment_sources:
            admissible = self._source_pool_for(environment_sources, q.key, q.family)
            if not admissible:
                continue
            evidence = self._evidence_context(
                admissible,
                TargetProject(q.key, q.family, q.X),
            )
            if evidence is None:
                continue
            episodes.append(Episode(evidence.c, evidence.z, q.y))
        return episodes

    def _run_environment(
        self,
        environment_sources: Sequence[SourceProject],
        target: TargetProject,
        omitted_family: str,
    ):
        episodes = self._episodes(environment_sources)
        if not episodes:
            return None
        target_evidence = self._evidence_context(environment_sources, target)
        if target_evidence is None:
            return None
        model = _HierarchicalRiskModel(
            self.quadrature_orders,
            self.quadrature_tol,
            self.hierarchical_max_iter,
        ).fit(episodes)
        q = model.predict(target_evidence.c, target_evidence.z)
        p_h = target_evidence.p_h
        p_u = target_evidence.p_u
        delta = p_h - p_u
        utility = delta * (2.0 * q - p_h - p_u)
        low = np.minimum(p_h, p_u)
        high = np.maximum(p_h, p_u)
        probability = np.clip(q, low, high)
        gate = np.full(len(q), 0.5, dtype=float)
        mask = np.abs(delta) > self.epsilon
        gate[mask] = np.clip((q[mask] - p_u[mask]) / delta[mask], 0.0, 1.0)
        coverage = len(target_evidence.contributing_families) / len(target_evidence.candidate_families)
        return EnvironmentResult(
            omitted_family=str(omitted_family),
            probability=probability,
            conditional_risk=q,
            transfer_utility=utility,
            gate=gate,
            p_h=p_h,
            p_u=p_u,
            coverage=float(coverage),
            contributing_families=target_evidence.contributing_families,
            candidate_families=target_evidence.candidate_families,
        )

    def fit_predict(self, sources: Sequence[SourceProject], target: TargetProject) -> HUGResult:
        sources = [self._validate_source(s) for s in sources]
        target = self._validate_target(target)
        eligible = self._source_pool_for(sources, target.key, target.family)
        families = tuple(sorted({s.family for s in eligible}))
        if len(families) < 4:
            raise RuntimeError("HUG-HDP requires at least four eligible candidate source families for matched episodic prediction.")
        results = []
        for omitted in families:
            environment_sources = [s for s in eligible if s.family != omitted]
            result = self._run_environment(environment_sources, target, omitted)
            if result is not None:
                results.append(result)
        if not results:
            raise RuntimeError("Target is uncovered because no matched environment produced valid heterogeneous-transfer evidence.")
        probability = np.mean(np.vstack([r.probability for r in results]), axis=0)
        return HUGResult(probability=np.clip(probability, 0.0, 1.0), environments=tuple(results))


__all__ = [
    "SourceProject",
    "TargetProject",
    "EnvironmentResult",
    "HUGResult",
    "HUGHDP",
]
