# Experiment Organization

**Type**: Feature Documentation
**Context**: Data organization for facial microexpression analysis
**Tags**: experiments, tests, baseline, data-organization
**Related**: [[ui_refactoring]], [[system_overview]]
**Updated**: 2025-01-28T14:30:00Z

## Feature Overview

The system now organizes facial landmark data hierarchically by experiments and tests, supporting machine learning model training and analysis.

### Data Structure
```
data/read/
├── experiment1/
│   ├── test1-baseline.csv
│   ├── test2.csv
│   └── test3.csv
├── experiment2/
│   ├── test1-baseline.csv
│   └── test2.csv
└── experiment3/
    ├── baseline.csv
    └── trial1.csv
```

### Key Components

#### 1. Experiment Selection
- Numerically sorted experiment folders
- Clear dropdown interface
- Automatic detection of experiment directories

#### 2. Test Selection
- Prioritizes baseline tests (automatically selected)
- Organized dropdown with baseline first
- Clear test naming conventions

### Machine Learning Context

The organization supports:
- Training data collection by experiment
- Baseline comparisons for each subject
- Trial prediction capabilities
- Personalized model development

## Implementation Details

### Sorting Logic
- Experiments sorted numerically when possible
- Falls back to alphabetical sorting
- Special handling for baseline tests

### Test Organization
- Baseline tests automatically detected
- Baseline tests always appear first in selection
- Other tests sorted alphabetically

## Usage Guidelines

### Naming Conventions
1. **Experiments**: Use numeric prefixes (e.g., "01_subject", "02_subject")
2. **Baseline Tests**: Append "-baseline" suffix
3. **Trial Tests**: Use consistent naming pattern

### Best Practices
- Always include baseline test in each experiment
- Maintain consistent test naming across experiments
- Use descriptive experiment names

## Future Enhancements

### Planned Features
- Automated test categorization
- Trial prediction models
- Cross-experiment analysis
- Personalized model training

### Integration Points
- Machine learning pipeline integration
- Automated feature extraction
- Model training workflow
- Results visualization

## Technical Notes

### File Organization
- All experiments under `data/read/`
- Consistent CSV format required
- Automatic file type validation

### Data Flow
1. User selects experiment
2. System identifies baseline
3. Tests presented in organized dropdown
4. Data loaded for analysis/training

## Success Metrics

### Organization
- ✅ Clear experiment hierarchy
- ✅ Automatic baseline detection
- ✅ Intuitive test selection
- ✅ Consistent naming support

### User Experience
- ✅ Two-click selection process
- ✅ Clear visual hierarchy
- ✅ Informative feedback
- ✅ Logical organization

## Metadata
- Created: 2025-01-28T14:30:00Z
- Updated: 2025-01-28T14:30:00Z
- Status: Active
- Priority: High 