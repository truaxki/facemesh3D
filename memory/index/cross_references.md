# Cross References Guide

**Type**: Index/Navigation
**Context**: Document relationships and navigation within the memory system
**Tags**: navigation, relationships, cross-reference
**Related**: All memory documents

## Document Relationship Map

### Core System Understanding
```
architecture/system_overview.md
    ├── components/streamlit_interface.md
    ├── components/animation_player.md
    ├── workflows/export_pipeline.md
    └── features/* (all feature implementations)
```

### Feature Implementation Chain
```
features/facial_landmark_import.md
    ├── features/z_scaling_enhancement.md
    ├── features/data_filtering.md
    ├── features/post_filter_movement.md
    ├── features/custom_baseline_functionality.md
    └── features/interactive_animation.md
```

### Technical Reports and Analysis
```
notes/baseline_definition_report.md
    ├── features/custom_baseline_functionality.md
    ├── features/data_filtering.md
    └── components/data_filters.py (implementation)
```

### Problem-Solution History
```
issues/ui_redesign_history.md
    ├── features/interface_cleanup.md
    ├── user_interactions/current_session.md
    └── workflows/export_pipeline.md (stalling fix)
```

## Navigation by Task

### 🎯 Getting Started
1. `memory/README.md` - Memory system overview
2. `index/quick_reference.md` - Essential information
3. `architecture/system_overview.md` - System understanding
4. `index/glossary.md` - Technical terms

### 🔧 Understanding Components
- **Web Interface**: `components/streamlit_interface.md`
- **Animation Player**: `components/animation_player.md`
- **Export System**: `workflows/export_pipeline.md`

### 📊 Working with Features
- **CSV Import**: `features/facial_landmark_import.md`
- **Z-Scaling**: `features/z_scaling_enhancement.md` + `features/optimal_z_scaling_discovery.md`
- **Filtering**: `features/data_filtering.md`
- **Baseline Selection**: `features/custom_baseline_functionality.md`
- **Movement Analysis**: `features/post_filter_movement.md`
- **Animation**: `features/interactive_animation.md`

### 📋 Technical Reports
- **Baseline Methodology**: `notes/baseline_definition_report.md`
- **Implementation Details**: Related feature documentation

### 🐛 Solving Problems
- **UI Issues**: `issues/ui_redesign_history.md`
- **Export Problems**: `workflows/export_pipeline.md`
- **General Issues**: `issues/resolved_issues.md` (if exists)

### 👤 User Context
- **Preferences**: `user_interactions/current_session.md`
- **Patterns**: `user_interactions/interaction_patterns.md` (if exists)

### 🚀 Development
- **Refactoring**: `development/refactor_summary.md`
- **Architecture**: `architecture/new_architecture_readme.md`
- **Standards**: `development/coding_standards.md` (if exists)

## Document Dependencies

### Critical Dependencies
These documents are referenced by many others:
- `index/quick_reference.md` - Referenced by all
- `user_interactions/current_session.md` - User context
- `architecture/system_overview.md` - System foundation

### Feature Dependencies
```
facial_landmark_import.md
    └─> z_scaling_enhancement.md
        └─> data_filtering.md
            ├─> custom_baseline_functionality.md
            └─> post_filter_movement.md
                └─> interactive_animation.md
```

### Technical Report Dependencies
```
notes/baseline_definition_report.md
    ├─> features/custom_baseline_functionality.md
    ├─> features/data_filtering.md
    └─> components/data_filters.py (source code)
```

### Workflow Dependencies
```
export_pipeline.md
    ├── components/streamlit_interface.md
    ├── issues/ui_redesign_history.md (emoji stalling)
    └── features/interface_cleanup.md
```

## Tag-Based Navigation

### #user-preferences
- `user_interactions/current_session.md`
- `issues/ui_redesign_history.md`
- `index/quick_reference.md`

### #technical-implementation
- `components/animation_player.md`
- `features/data_filtering.md`
- `features/custom_baseline_functionality.md`
- `features/post_filter_movement.md`

### #technical-reports
- `notes/baseline_definition_report.md`

### #baseline-analysis
- `notes/baseline_definition_report.md`
- `features/custom_baseline_functionality.md`
- `features/data_filtering.md`

### #problem-solution
- `issues/ui_redesign_history.md`
- `workflows/export_pipeline.md`
- `features/interface_cleanup.md`

### #architecture
- `architecture/system_overview.md`
- `architecture/new_architecture_readme.md`
- `development/refactor_summary.md`

### #visualization
- `features/interactive_animation.md`
- `components/animation_player.md`
- `features/animation_views_update.md`

### #data-processing
- `features/facial_landmark_import.md`
- `features/data_filtering.md`
- `features/custom_baseline_functionality.md`
- `features/post_filter_movement.md`
- `notes/baseline_definition_report.md`

## Quick Links by Component

### Streamlit Interface
- Main Doc: `components/streamlit_interface.md`
- Related:
  - `issues/ui_redesign_history.md`
  - `features/interface_cleanup.md`
  - `workflows/export_pipeline.md`

### Animation System
- Main Doc: `components/animation_player.md`
- Related:
  - `features/interactive_animation.md`
  - `workflows/frame_by_frame_guide.md`
  - `features/animation_views_update.md`

### Data Import/Processing
- Main Docs:
  - `features/facial_landmark_import.md`
  - `features/data_filtering.md`
  - `features/custom_baseline_functionality.md`
- Technical Reports:
  - `notes/baseline_definition_report.md`
- Related:
  - `features/z_scaling_enhancement.md`
  - `features/post_filter_movement.md`

### Export System
- Main Doc: `workflows/export_pipeline.md`
- Related:
  - `issues/ui_redesign_history.md` (emoji fix)
  - `components/streamlit_interface.md`

## Historical Evolution

### Feature Development Timeline
1. Basic point cloud visualization
2. `facial_landmark_import.md` - CSV support added
3. `z_scaling_enhancement.md` - Depth enhancement
4. `data_filtering.md` - Kabsch alignment
5. `custom_baseline_functionality.md` - Flexible baseline selection
6. `post_filter_movement.md` - Movement analysis
7. `interactive_animation.md` - Enhanced player
8. `interface_cleanup.md` - UI optimization

### Technical Documentation Evolution
1. `notes/baseline_definition_report.md` - Baseline methodology documentation

### Major Refactors
1. `development/refactor_summary.md` - System consolidation
2. `architecture/new_architecture_readme.md` - Architecture update
3. `issues/ui_redesign_history.md` - UI evolution

## Usage Patterns

### For New Features
1. Check `user_interactions/current_session.md`
2. Review similar features in `features/`
3. Follow patterns from `components/`
4. Update relevant cross-references

### For Technical Understanding
1. Start with relevant `notes/` reports
2. Review `features/` for implementation details
3. Check `components/` for code structure
4. Reference `index/glossary.md` for terms

### For Bug Fixes
1. Check `issues/` for similar problems
2. Review related `workflows/`
3. Test with patterns from feature docs
4. Document solution if significant

### For Understanding
1. Start with `architecture/system_overview.md`
2. Deep dive into specific `components/`
3. Review `features/` for implementations
4. Check technical reports in `notes/`
5. Reference `index/glossary.md` for terms

## Metadata
- Created: 2025-01-24T18:15:00Z
- Updated: 2025-01-28T15:35:00Z
- Confidence: High
- Source: Complete memory system analysis with notes section 