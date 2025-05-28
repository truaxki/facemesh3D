# 🧠 Facemesh Point Cloud Visualization - Memory System

This directory contains the complete knowledge base and documentation for the facemesh point cloud visualization system. It serves as the institutional memory for understanding, maintaining, and extending the codebase.

## 📁 Directory Structure

```
memory/
├── README.md                          # This file - Memory system overview
├── architecture/                      # System design and technical architecture
│   ├── system_overview.md            # High-level system architecture
│   └── technical_details.md          # Deep technical implementation details
├── components/                        # Individual component documentation
│   ├── streamlit_interface.md        # Web UI component details
│   ├── animation_player.md           # Animation player implementation
│   └── point_cloud_processing.md     # Point cloud processing algorithms
├── workflows/                         # Process and pipeline documentation
│   ├── export_pipeline.md            # Video export workflow
│   ├── data_import_workflow.md       # Data import and processing
│   └── filtering_pipeline.md         # Data filtering workflows
├── features/                          # Feature-specific documentation
│   ├── facial_landmark_import.md     # Facial landmark CSV import
│   ├── z_scaling_enhancement.md      # Z-axis scaling implementation
│   ├── post_filter_movement.md       # Post-filter movement analysis
│   ├── interactive_animation.md      # Interactive animation features
│   └── data_filtering.md             # Kabsch alignment and filters
├── issues/                            # Problem history and solutions
│   ├── ui_redesign_history.md        # UI evolution and decisions
│   └── resolved_issues.md            # Past issues and their solutions
├── user_interactions/                 # User preferences and session data
│   ├── current_session.md            # Current user preferences
│   └── interaction_patterns.md       # Common user interaction patterns
├── development/                       # Development guidelines
│   ├── coding_standards.md           # Code style and patterns
│   ├── testing_guide.md              # Testing approaches
│   └── deployment_guide.md           # Deployment procedures
└── index/                            # Quick access and navigation
    ├── quick_reference.md            # Essential information cheat sheet
    ├── cross_references.md           # Document relationships
    └── glossary.md                   # Technical terms and concepts
```

## 🎯 Purpose

This memory system serves multiple critical functions:

1. **Knowledge Preservation**: Captures implementation details, design decisions, and solutions
2. **Context Transfer**: Enables new developers/AI agents to quickly understand the system
3. **Pattern Documentation**: Records successful patterns and anti-patterns
4. **User Understanding**: Maintains user preferences and interaction history
5. **Problem Solving**: Archives issues and their solutions for future reference

## 🚀 Quick Start Guide

### For New Developers/AI Agents:

1. **Start Here**: Read `index/quick_reference.md` for immediate context
2. **Understand User**: Check `user_interactions/current_session.md` for preferences
3. **System Overview**: Review `architecture/system_overview.md` for big picture
4. **Deep Dive**: Explore specific components/features as needed

### For Specific Tasks:

- **Fixing Export Issues**: See `workflows/export_pipeline.md`
- **UI Changes**: MUST read `issues/ui_redesign_history.md` first
- **Adding Features**: Check `development/coding_standards.md`
- **Understanding Filters**: See `features/data_filtering.md`

## 📋 Key Documents

### Essential Reading:
- `index/quick_reference.md` - Critical information at a glance
- `user_interactions/current_session.md` - User preferences and requirements
- `architecture/system_overview.md` - System architecture understanding

### Feature Documentation:
- `features/facial_landmark_import.md` - CSV import implementation
- `features/post_filter_movement.md` - Movement analysis system
- `features/interactive_animation.md` - Animation player details

### Problem Solving:
- `issues/ui_redesign_history.md` - UI evolution and decisions
- `issues/resolved_issues.md` - Common problems and solutions

## 🔍 Navigation Tips

1. **Use Cross References**: `index/cross_references.md` shows document relationships
2. **Check Glossary**: `index/glossary.md` explains technical terms
3. **Follow Tags**: Documents include tags for related content
4. **Update Dates**: Check document timestamps for currency

## ⚠️ Critical Rules

1. **Always Check Memory First**: Before making changes, review relevant documentation
2. **Update After Changes**: Document significant changes in appropriate sections
3. **Respect User Preferences**: Always honor documented user preferences
4. **Follow Established Patterns**: Use proven patterns from the documentation

## 📊 Document Metadata

Each document includes:
- **Type**: Category (Architecture, Component, Workflow, etc.)
- **Context**: When/why to use this document
- **Tags**: Related topics for cross-referencing
- **Related**: Links to other relevant documents
- **Updated**: Last modification timestamp

## 🔄 Maintenance

This memory system should be:
- **Living Documentation**: Update as the system evolves
- **Accurate**: Ensure documentation matches implementation
- **Accessible**: Keep language clear and structure logical
- **Complete**: Document all significant aspects

## 💡 Best Practices

1. **Document Immediately**: Capture knowledge while fresh
2. **Be Specific**: Include concrete examples and code snippets
3. **Link Liberally**: Connect related documents
4. **Version Aware**: Note which version changes apply to
5. **User Focused**: Remember the human using the system

---

*This memory system is the institutional knowledge of the facemesh visualization project. Treat it as the source of truth for understanding and extending the system.* 