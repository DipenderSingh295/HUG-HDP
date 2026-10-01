# HUG-HDP

**Replication package for HUG-HDP: Hierarchical Utility Gating for Heterogeneous Defect Prediction**

HUG-HDP is a heterogeneous defect prediction framework for the
zero-target-label setting. It combines heterogeneous-transfer evidence
with complementary target-structural evidence and uses source-only
development to determine how the two evidence streams should contribute
to the final prediction.

This repository provides the implementation and experimental resources
used in the empirical study and is intended to support reproducibility,
verification, and future research on heterogeneous defect prediction.

---

## Replication Package

The replication package contains the main resources required to reproduce
the study, including:

- dataset information and original references;
- detailed metric definitions for each dataset family;
- preprocessing scripts;
- implementation of HUG-HDP;
- source-target construction utilities;
- source-only development and validation utilities;
- evaluation scripts;
- statistical-analysis scripts;

---

## Study Setting

The study considers **zero-target-label heterogeneous defect prediction
(HDP)**.

For each target project, model development is performed using source-side
information only. Target labels are not used for:

- evidence construction;
- probability calibration;
- context construction;
- model development;
- model selection;
- classification-threshold selection; or
- target prediction.

Target labels are accessed only for final empirical evaluation.

---

## Datasets

The empirical study uses **25 projects from five public
defect-prediction dataset families**:

| Dataset Family | Number of Projects |
|---|---:|
| AEEEM | 5 |
| GitHub-Python | 3 |
| JIRA | 9 |
| PROMISE | 5 |
| ReLink | 3 |
| **Total** | **25** |

The dataset families differ in project size, metric dimensionality,
defect prevalence, and prediction-instance characteristics. This
provides multiple heterogeneous source-target environments for
evaluation.

### Original Dataset References

#### AEEEM

D'Ambros, M., Lanza, M., and Robbes, R.  
**Evaluating defect prediction approaches: A benchmark and an extensive
comparison.**  
*Empirical Software Engineering*, 17, 531-577, 2012.

#### GitHub-Python

Song, L., and Minku, L. L.  
**A procedure to continuously evaluate predictive performance of
just-in-time software defect prediction models during software
development.**  
*IEEE Transactions on Software Engineering*, 49(2), 646-666, 2022.

#### JIRA

Yatish, S., et al.  
**Mining software defects: Should we consider affected releases?**  
*Proceedings of the 41st International Conference on Software
Engineering (ICSE)*, 2019.

#### ReLink

Wu, R., et al.  
**ReLink: Recovering links between bugs and changes.**  
*Proceedings of the 19th ACM SIGSOFT Symposium and the 13th European
Conference on Foundations of Software Engineering*, 2011.

#### PROMISE

Menzies, T., Krishna, R., and Pryor, D.  
**The PROMISE Repository of Empirical Software Engineering Data**, 2015.

---

## Dataset and Metric Documentation

Because the dataset families use different feature spaces, the
replication package provides detailed metric documentation for each
family.

The documentation records:

- metric abbreviations;
- metric descriptions;
- dataset-specific feature information; and
- the heterogeneous feature spaces used during experimental
  construction.

The complete metric definitions used in the study are listed below.

---

<details>
<summary><b>AEEEM Metrics</b></summary>

| Abbreviation | Description |
|---|---|
| ck_oo_wmc | Weighted method count |
| ck_oo_dit | Depth of inheritance tree |
| ck_oo_rfc | Response for class |
| ck_oo_noc | Number of children |
| ck_oo_cbo | Coupling between objects |
| ck_oo_lcom | Lack of cohesion in methods |
| ck_oo_fanin | Number of other classes that reference the class |
| ck_oo_fanout | Number of other classes referenced by the class |
| ck_oo_noa | Number of attributes |
| ck_oo_nopa | Number of public attributes |
| ck_oo_nopra | Number of private attributes |
| ck_oo_noai | Number of attributes inherited |
| ck_oo_loc | Number of lines of code |
| ck_oo_nom | Number of methods |
| ck_oo_nopm | Number of public methods |
| ck_oo_noprm | Number of private methods |
| ck_oo_nomt | Number of methods inherited |
| WCHU_wmc | Weighted churn of weighted method count |
| WCHU_dit | Weighted churn of depth of inheritance tree |
| WCHU_rfc | Weighted churn of response for class |
| WCHU_noc | Weighted churn of number of children |
| WCHU_cbo | Weighted churn of coupling between objects |
| WCHU_lcom | Weighted churn of lack of cohesion in methods |
| WCHU_fanin | Weighted churn of number of other classes that reference the class |
| WCHU_fanout | Weighted churn of number of other classes referenced by the class |
| WCHU_noa | Weighted churn of number of attributes |
| WCHU_nopa | Weighted churn of number of public attributes |
| WCHU_nopra | Weighted churn of number of private attributes |
| WCHU_noai | Weighted churn of number of attributes inherited |
| WCHU_loc | Weighted churn of number of lines of code |
| WCHU_nom | Weighted churn of number of methods |
| WCHU_nopm | Weighted churn of number of public methods |
| WCHU_noprm | Weighted churn of number of private methods |
| WCHU_nomt | Weighted churn of number of methods inherited |
| LDHH_wmc | Linear decayed history entropy of weighted method count |
| LDHH_dit | Linear decayed history entropy of depth of inheritance tree |
| LDHH_rfc | Linear decayed history entropy of response for class |
| LDHH_noc | Linear decayed history entropy of number of children |
| LDHH_cbo | Linear decayed history entropy of coupling between objects |
| LDHH_lcom | Linear decayed history entropy of lack of cohesion in methods |
| LDHH_fanin | Linear decayed history entropy of number of other classes that reference the class |
| LDHH_fanout | Linear decayed history entropy of number of other classes referenced by the class |
| LDHH_noa | Linear decayed history entropy of number of attributes |
| LDHH_nopa | Linear decayed history entropy of number of public attributes |
| LDHH_nopra | Linear decayed history entropy of number of private attributes |
| LDHH_noai | Linear decayed history entropy of number of attributes inherited |
| LDHH_loc | Linear decayed history entropy of number of lines of code |
| LDHH_nom | Linear decayed history entropy of number of methods |
| LDHH_nopm | Linear decayed history entropy of number of public methods |
| LDHH_noprm | Linear decayed history entropy of number of private methods |
| LDHH_nomt | Linear decayed history entropy of number of methods inherited |
| CvsEntropy | Entropy of CVS change log |
| CvsWEntropy | Weighted entropy of CVS change log |
| CvsLogEntropy | Logarithmic entropy of CVS change log |
| CvsExpEntropy | Exponential entropy of CVS change log |
| CvsLinEntropy | Linear entropy of CVS change log |
| numberOfNonTrivialBugsFoundUntil | Number of non-trivial bugs found until the corresponding fix |
| numberOfCriticalBugsFoundUntil | Number of critical bugs found until the corresponding fix |
| numberOfHighPriorityBugsFoundUntil | Number of high-priority bugs found until the corresponding fix |
| numberOfMajorBugsFoundUntil | Number of major bugs found until the corresponding fix |
| numberOfBugsFoundUntil | Number of bugs found until the corresponding fix |

</details>

---

<details>
<summary><b>GitHub-Python Metrics</b></summary>

| Abbreviation | Description |
|---|---|
| fix | Whether or not the change is a defect fix |
| ns | Number of modified subsystems in the change |
| nd | Number of modified code directories |
| nf | Number of files modified |
| entropy | Distribution of code changes across files, computed using information entropy |
| la | Lines of code added |
| ld | Lines of code deleted |
| lt | Lines of code in a file before the change |
| ndev | Number of developers who previously modified the changed files |
| age | Average time interval between the last and current change |
| nuc | Number of unique prior changes to the modified files |
| exp | Developer overall experience |
| rexp | Developer recent experience |
| sexp | Developer experience within the modified subsystem |

</details>

---

<details>
<summary><b>JIRA Metrics</b></summary>

| Abbreviation | Description |
|---|---|
| AvgCyclomatic | Average cyclomatic complexity for all nested functions or methods |
| SumCyclomatic | Sum of cyclomatic complexity of all nested functions or methods |
| AvgCyclomaticModified | Average modified cyclomatic complexity for all nested functions or methods |
| SumCyclomaticModified | Sum of modified cyclomatic complexity of all nested functions |
| AvgCyclomaticStrict | Average strict cyclomatic complexity for all nested functions or methods |
| SumCyclomaticStrict | Sum of strict cyclomatic complexity of all nested functions or methods |
| AvgEssential | Average essential complexity for all nested functions or methods |
| SumEssential | Sum of essential complexity of all nested functions or methods |
| AvgLine | Average number of lines for all nested functions or methods |
| AvgLineBlank | Average number of blank lines for all nested functions or methods |
| AvgLineCode | Average number of lines containing source code |
| AvgLineComment | Average number of comment lines |
| CountClassBase | Number of immediate base classes |
| CountClassCoupled | Number of other classes coupled to |
| CountClassDerived | Number of immediate subclasses |
| MaxInheritanceTree | Maximum depth of class in inheritance tree |
| PercentLackOfCohesion | 100% minus the average cohesion for package entities |
| CountDeclClass | Number of classes |
| CountDeclClassMethod | Number of class methods |
| CountDeclClassVariable | Number of class variables |
| CountDeclFunction | Number of functions |
| CountDeclInstanceMethod | Number of instance methods |
| CountDeclInstanceVariable | Number of instance variables |
| CountDeclMethod | Number of local non-inherited methods |
| CountDeclMethodDefault | Number of local default methods |
| CountDeclMethodPrivate | Number of local private methods |
| CountDeclMethodProtected | Number of local protected methods |
| CountDeclMethodPublic | Number of local public methods |
| CountLine | Number of physical lines |
| CountLineBlank | Number of blank lines |
| CountLineCode | Number of lines containing source code |
| CountLineCodeDecl | Number of lines containing declarative source code |
| CountLineCodeExe | Number of lines containing executable source code |
| CountLineComment | Number of comment lines |
| CountSemicolon | Number of semicolons |
| CountStmt | Number of statements |
| CountStmtDecl | Number of declarative statements |
| CountStmtExe | Number of executable statements |
| MaxCyclomatic | Maximum cyclomatic complexity |
| MaxCyclomaticModified | Maximum modified cyclomatic complexity |
| MaxCyclomaticStrict | Maximum strict cyclomatic complexity |
| RatioCommentToCode | Ratio of comment lines to code lines |
| CountInput_Min | Minimum number of calling subprograms plus global variables read |
| CountInput_Mean | Mean number of calling subprograms plus global variables read |
| CountInput_Max | Maximum number of calling subprograms plus global variables read |
| CountOutput_Min | Minimum number of called subprograms plus global variables set |
| CountOutput_Mean | Mean number of called subprograms plus global variables set |
| CountOutput_Max | Maximum number of called subprograms plus global variables set |
| CountPath_Min | Minimum number of unique paths through a body of code |
| CountPath_Mean | Mean number of unique paths through a body of code |
| CountPath_Max | Maximum number of unique paths through a body of code |
| MaxNesting_Min | Minimum of maximum nesting level |
| MaxNesting_Mean | Mean of maximum nesting level |
| MaxNesting_Max | Maximum of maximum nesting level |
| COMM | Number of Git commits |
| ADDED_LINES | Normalized number of lines added |
| DEL_LINES | Normalized number of lines deleted |
| ADEV | Number of active developers |
| DDEV | Number of distinct developers |
| MINOR_COMMIT | Developers contributing less than 5% of total code changes |
| MINOR_LINE | Developers contributing less than 5% of total LOC |
| MAJOR_COMMIT | Developers contributing more than 5% of total code changes |
| MAJOR_LINES | Developers contributing more than 5% of total LOC |
| OWN_COMMIT | Proportion of code changes by top contributor |
| OWN_LINE | Proportion of lines of code by top contributor |

</details>

---

<details>
<summary><b>ReLink Metrics</b></summary>

| Abbreviation | Description |
|---|---|
| AvgCyclomatic | Average cyclomatic complexity |
| AvgCyclomaticModified | Average modified cyclomatic complexity |
| AvgCyclomaticStrict | Average strict cyclomatic complexity |
| AvgEssential | Average essential complexity |
| AvgLine | Average lines |
| AvgLineBlank | Average blank lines |
| AvgLineCode | Average code lines |
| AvgLineComment | Average comment lines |
| CountLine | Number of lines |
| CountLineBlank | Number of blank lines |
| CountLineCode | Number of code lines |
| CountLineCodeDecl | Number of declarative code lines |
| CountLineCodeExe | Number of executable code lines |
| CountLineComment | Number of comment lines |
| CountSemicolon | Number of semicolons |
| CountStmt | Number of statements |
| CountStmtDecl | Number of declarative statements |
| CountStmtExe | Number of executable statements |
| MaxCyclomatic | Maximum cyclomatic complexity |
| MaxCyclomaticModified | Maximum modified cyclomatic complexity |
| MaxCyclomaticStrict | Maximum strict cyclomatic complexity |
| RatioCommentToCode | Ratio of comment lines to code lines |
| SumCyclomatic | Sum of cyclomatic complexity |
| SumCyclomaticModified | Sum of modified cyclomatic complexity |
| SumCyclomaticStrict | Sum of strict cyclomatic complexity |
| SumEssential | Sum of essential complexity |

</details>

---

<details>
<summary><b>PROMISE Metrics</b></summary>

| Abbreviation | Description |
|---|---|
| WMC | Weighted Methods per Class |
| DIT | Depth of Inheritance Tree |
| NOC | Number of Children |
| CBO | Coupling Between Object Classes |
| RFC | Response for a Class |
| LCOM | Lack of Cohesion in Methods |
| CA | Afferent Couplings |
| CE | Efferent Couplings |
| NPM | Number of Public Methods |
| LCOM3 | Lack of Cohesion in Methods (variant of LCOM) |
| LOC | Lines of Code |
| DAM | Data Access Metric |
| MOA | Measure of Aggregation |
| MFA | Measure of Functional Abstraction |
| CAM | Cohesion Among Methods of a Class |
| IC | Inheritance Coupling |
| CBM | Coupling Between Methods |
| AMC | Average Method Complexity |
| CC | McCabe's Cyclomatic Complexity |
| MAX_CC | Maximum value of CC among methods in the class |
| AVG_CC | Average CC of methods in the class |

</details>

---

## Dataset Overlap Audit

Dataset-family and project identities are checked during experimental
preparation to reduce unintended overlap between source-side development
and target evaluation.

The replication package includes the **overlap audit used for the
reported experiments**.

Any overlap exclusion that is **verified and actually applied** during
experimental construction is documented in the corresponding replication
material. Projects are not removed solely because they have similar
names; an exclusion is recorded only when the relevant relationship is
verified.

This makes the source-target construction process transparent without
assuming unverified overlap between datasets.

---

## Preprocessing

The replication package includes the preprocessing scripts used to
prepare the datasets for the experiments.

At a high level, preprocessing includes:

- project loading and validation;
- identification of predictors and defect labels;
- dataset-specific feature preparation;
- construction of source and target datasets;
- preparation of source-only development environments; and
- generation of inputs required by the heterogeneous prediction
  pipeline.

The exact preprocessing operations used for the reported experiments are
implemented in the corresponding scripts and configuration files.

---

## HUG-HDP Implementation

The repository provides the implementation of the proposed HUG-HDP
framework.

At a high level, the implementation contains the following stages:

1. construction of heterogeneous-transfer evidence;
2. construction and source-side calibration of target-structural
   evidence;
3. source-only pseudo-target environment construction;
4. project-level and prediction-instance-level context construction;
5. hierarchical conditional-risk estimation;
6. utility-guided evidence arbitration; and
7. final target prediction.

The complete procedure follows the zero-target-label protocol described
in the paper.

Mathematical definitions and methodological justification are provided
in the manuscript, while the executable realization is contained in the
replication package.

---

## Heterogeneous Transfer and Feasibility

The heterogeneous-transfer component operates on feasible source-target
relationships.

If a required heterogeneous source-target relationship cannot be formed
under the experimental matching conditions, that relationship is treated
as **infeasible**.

No artificial transfer score or fabricated prediction is assigned to an
infeasible relationship.

Only valid environments contribute to the corresponding aggregated
target prediction.

Coverage information is retained so that transfer feasibility can also
be examined during robustness analysis.

---

## Source-Only Development

The complete HUG-HDP framework is developed from source-side information.

Source projects are used as pseudo-target environments during model
development. The experimental construction preserves project and
dataset-family separation between development and final target
evaluation.

The validation procedure is also source-only. Information from the final
target labels is not used to determine:

- calibrators;
- context transformations;
- hierarchical-model parameters;
- experiment selection; or
- the F1 classification threshold.


---

## Performance Measures

The primary predictive measures are:

### AUC

AUC measures the ability of a prediction model to discriminate between
defective and non-defective instances across classification thresholds.

Higher AUC indicates better discrimination.

### F1

F1 summarizes the balance between precision and recall for binary defect
classification.

The F1 classification threshold is selected exclusively from feasible
source-side validation predictions and is fixed before final target
evaluation.

Target labels therefore do not participate in threshold selection.

Mechanism-specific utility quantities are used separately in the RQ3
analysis and are not treated as primary comparative performance
measures.

---

## Research Questions and Reproduction Resources

The replication package supports all four empirical research questions
reported in the paper.

### RQ1 — Comparison with Existing HDP Methods

RQ1 evaluates HUG-HDP against the five comparison methods using
project-level AUC and F1.

The corresponding analysis resources include:

- project-level performance aggregation;
- win/tie/loss summaries;
- Friedman tests;
- paired Wilcoxon signed-rank tests;
- Benjamini-Hochberg correction; and
- matched-pairs rank-biserial effect sizes.

---

### RQ2 — Contribution of HUG-HDP Components

RQ2 examines the contribution of the main framework components.

The replication resources support the following variants:

- complete HUG-HDP;
- without project context;
- without prediction-instance context;
- without hierarchy;
- without projection;
- heterogeneous-transfer evidence only; and
- target-structural evidence only.

Each variant follows the same source-only experimental principle, and
its F1 threshold is selected from its corresponding source-side
validation predictions.

---

### RQ3 — Transfer-Utility Analysis

RQ3 examines whether estimated transfer utility reflects the observed
relative utility of heterogeneous-transfer and target-structural
evidence.

The provided analysis resources support:

- estimated-utility ordering;
- project-balanced utility summaries;
- estimated-versus-observed evidence-preference analysis;
- project-level utility association analysis; and
- project-bootstrap uncertainty summaries used in the reported
  mechanism analysis.

The Brier-derived utility used here is specific to the mechanism analysis
and is separate from the primary AUC/F1 comparison.

---

### RQ4 — Robustness and Boundary Conditions

RQ4 examines how the benefit of HUG-HDP changes under different transfer
conditions.

The package contains resources for analyzing:

- mean source-target distribution shift;
- covariance shift;
- evidence disagreement; and
- feasible heterogeneous-transfer coverage.

The corresponding scripts produce the project-level summaries and
boundary-condition figures reported in the manuscript.

---

## Statistical Analysis

For the multi-method comparison in RQ1, the target project is treated as
the statistical unit.

The replication package includes resources for:

- the Friedman test for overall multi-method differences;
- paired Wilcoxon signed-rank comparisons;
- Benjamini-Hochberg correction for multiple comparisons; and
- matched-pairs rank-biserial effect sizes.

RQ2, RQ3, and RQ4 are interpreted primarily through descriptive,
mechanism, and boundary-condition analyses rather than additional
hypothesis-testing procedures.

