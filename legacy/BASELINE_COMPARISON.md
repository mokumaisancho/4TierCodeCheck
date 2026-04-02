# Baseline Comparison Guide

## Overview

This document provides guidance for comparing the 4-Tiers CodeCheck system against established code analysis tools and datasets.

## Comparison Targets

### 1. Static Analysis Tools (Direct Competitors)

#### Radon (Python Complexity)
- **Repository**: https://github.com/rubik/radon
- **Metrics**: Cyclomatic complexity, raw metrics, Halstead metrics, Maintainability Index
- **Comparison Points**:
  - Feature F (Complexity Trajectory) vs Radon cyclomatic complexity
  - Correlation between knot score and Radon MI
  - Speed comparison

```python
# Comparison method
import radon
from radon.complexity import cc_visit
from static_code_knot_analyzer import StaticCodeKnotAnalyzer

# Analyze same file with both
code = open('test.py').read()

# Radon
radon_cc = cc_visit(code)
radon_mi = mi_visit(code, multi=True)

# 4-Tiers
analyzer = StaticCodeKnotAnalyzer('test.py')
knot_result = analyzer.analyze()

# Compare: Does Feature F correlate with Radon CC?
```

#### Pylint (Python Linting)
- **Repository**: https://github.com/PyCQA/pylint
- **Metrics**: Code smells, anti-patterns, style issues
- **Comparison Points**:
  - Feature H (Distortions) vs Pylint anti-patterns
  - Feature C (Contradiction) vs logical issues
  - Overlap in detection capabilities

#### SonarQube / SonarCloud
- **Website**: https://www.sonarqube.org/
- **Metrics**: Technical debt, code coverage, bugs, vulnerabilities
- **Comparison Points**:
  - Feature D (Expansion Stop) vs SonarQube code coverage
  - Technical Debt Index vs Knot Score
  - Issue severity mapping

#### CodeClimate
- **Website**: https://codeclimate.com/
- **Metrics**: Complexity, duplication, churn
- **Comparison Points**:
  - Feature A (Regression/Duplication) vs duplication detection
  - Feature F vs complexity metrics

### 2. Academic Datasets (Validation)

#### PROMISE Dataset
- **URL**: http://promise.site.uottawa.ca/SERepository/datasets-page
- **Description**: Large collection of software engineering datasets
- **Use Cases**:
  - Validate complexity calculations (Feature F)
  - Compare defect prediction vs knot detection
  - Statistical correlation analysis

#### Technical Debt Dataset
- **Paper**: "Self-Admitted Technical Debt"
- **Use Cases**:
  - Validate Feature E (Question Cutoff/TODO detection)
  - Compare comment-based detection

#### Defects4J
- **Repository**: https://github.com/rjust/defects4j
- **Description**: Database of real bugs from Java projects
- **Use Cases**:
  - Do files with high knot scores have more bugs?
  - Validate as a predictor of code quality

### 3. GitHub Repositories (Similar Projects)

| Repository | Description | Comparison Point |
|------------|-------------|------------------|
| [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) | Opinionated Python linter | Feature overlap |
| [flake8](https://github.com/PyCQA/flake8) | Python style guide enforcement | Speed, coverage |
| [prospector](https://github.com/PyCQA/prospector) | Meta-linter combining tools | Aggregate comparison |
| [code2vec](https://github.com/tech-srl/code2vec) | Neural code embeddings | Novelty comparison |
| [DeepBugs](https://github.com/michaelpradel/DeepBugs) | Learning bug patterns | ML approach comparison |

## Comparison Methodology

### 1. Metrics Correlation Study

```python
# Example comparison script
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr

# Collect data on multiple files
data = []
for file in test_files:
    # 4-Tiers
    analyzer = StaticCodeKnotAnalyzer(file)
    knot_result = analyzer.analyze()
    
    # Radon
    code = open(file).read()
    radon_cc = max(block.complexity for block in cc_visit(code))
    radon_mi = mi_visit(code, multi=True)
    
    # Pylint
    pylint_score = run_pylint(file)  # 0-10 scale
    
    data.append({
        'file': file,
        'knot_score': knot_result.knot_score,
        'feature_f': knot_result.features['F'],
        'radon_cc': radon_cc,
        'radon_mi': radon_mi,
        'pylint': pylint_score
    })

df = pd.DataFrame(data)

# Calculate correlations
corr_knot_radon, _ = pearsonr(df['knot_score'], df['radon_cc'])
corr_f_radon, _ = pearsonr(df['feature_f'], df['radon_cc'])

print(f"Knot Score vs Radon CC: {corr_knot_radon:.3f}")
print(f"Feature F vs Radon CC: {corr_f_radon:.3f}")
```

### 2. Detection Accuracy Study

Use labeled datasets (e.g., code smells, bugs):

```python
# Precision/Recall comparison
def evaluate_detection(ground_truth, predictions):
    tp = sum(1 for g, p in zip(ground_truth, predictions) if g and p)
    fp = sum(1 for g, p in zip(ground_truth, predictions) if not g and p)
    fn = sum(1 for g, p in zip(ground_truth, predictions) if g and not p)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {'precision': precision, 'recall': recall, 'f1': f1}

# Compare tools on same dataset
results_4tiers = evaluate_detection(ground_truth, four_tiers_predictions)
results_pylint = evaluate_detection(ground_truth, pylint_predictions)
results_sonar = evaluate_detection(ground_truth, sonar_predictions)
```

### 3. Performance Benchmark

```python
import time

def benchmark_tool(tool_func, files):
    times = []
    for f in files:
        start = time.perf_counter()
        tool_func(f)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    return np.mean(times), np.std(times)

# Benchmark each tool
mean_4tiers, std_4tiers = benchmark_tool(analyze_with_4tiers, test_files)
mean_radon, std_radon = benchmark_tool(analyze_with_radon, test_files)
mean_pylint, std_pylint = benchmark_tool(analyze_with_pylint, test_files)

print(f"4-Tiers: {mean_4tiers*1000:.2f} ± {std_4tiers*1000:.2f} ms")
print(f"Radon: {mean_radon*1000:.2f} ± {std_radon*1000:.2f} ms")
print(f"Pylint: {mean_pylint*1000:.2f} ± {std_pylint*1000:.2f} ms")
```

## Expected Correlations

Based on the 8-feature model, we expect:

| Our Feature | Tool Metric | Expected Correlation |
|-------------|-------------|---------------------|
| Feature A (Duplication) | Radon raw metrics (duplicated lines) | High (0.7-0.9) |
| Feature B (Isomorphism) | Pylint similarity checker | Medium (0.5-0.7) |
| Feature C (Contradiction) | Bandit security issues | Low-Medium (0.3-0.5) |
| Feature D (Expansion Stop) | SonarQube coverage | High negative (-0.7) |
| Feature E (TODOs) | grep -r "TODO\|FIXME" | High (0.8+) |
| Feature F (Complexity) | Radon cyclomatic complexity | High (0.8+) |
| Feature H (Distortions) | Pylint warnings | Medium (0.5-0.7) |
| Knot Score (overall) | SonarQube Technical Debt Index | Medium-High (0.6-0.8) |

## Unique Differentiators

What makes 4-Tiers different from these tools:

1. **Psychological Model**: Only tool using repurposed therapy model
2. **8-Feature Integration**: Combines multiple dimensions vs single metrics
3. **Temporal Analysis**: Git history integration (similar to CodeScene)
4. **Predictive**: Pre-necessity detection vs just current state
5. **Knot-Explosion-Insight**: Novel metaphor for code evolution

## Papers for Citation

When comparing, cite these foundational works:

### Our Approach
- Tang & DeRubeis (1999) - Sudden Gains in Therapy (original knot model)
- Wallas (1926) - 4-Stage Creativity Model

### Comparison Baselines
- McCabe (1976) - Cyclomatic Complexity (Radon baseline)
- Halstead (1977) - Software Metrics (complexity baseline)
- Marinescu (2004) - Detection Strategies for Code Smells
- Rahman et al. (2012) - Bug prediction vs code smells

### Tool Evaluations
- Nagappan et al. (2006) - Mining Metrics to Predict Component Failures
- Beller et al. (2016) - Analyzing the State of Static Analysis
- Pascarella & Bacchelli (2017) - Classifying Code Comments

## Next Steps

1. **Install comparison tools**:
   ```bash
   pip install radon pylint bandit
   ```

2. **Collect test corpus**:
   - 50-100 Python files of varying complexity
   - Include known problematic files (if available)

3. **Run comparison study**:
   - Use the scripts in this document
   - Generate correlation matrix
   - Create visualization

4. **Document findings**:
   - Add results to patent application
   - Identify unique value propositions
   - Quantify accuracy/speed trade-offs
