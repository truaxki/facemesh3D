# System Prompt: Facemesh Point Cloud Visualization

This codebase is a **facial microexpression analysis tool** using 3D point cloud visualization.

## Directory Structure & Organization Rules

### User Data Flow
- **Input**: Place CSV files in `data/read/`
- **Output**: All animations saved to `data/write/`
- **NEVER** save new animations to `/animations/` (legacy directory)

### File Organization Rules
1. **Test Files**: Save directly to `cleanup_archive/test_files/`
2. **Temporary Scripts**: Use `cleanup_archive/temp_scripts/`
3. **Old Versions**: Move to `cleanup_archive/old_versions/`
4. **Documentation**: Update in `memory/` subdirectories
5. **Cache Files**: Delete immediately (no __pycache__ commits)

### Core Workflow
- Streamlined 2-click process: Import CSV → Create Animation
- Automatic Kabsch alignment for head motion removal
- Local movement visualization for microexpressions
- All outputs include metadata.json

### Development Guidelines
- Keep root directory clean - no test files or captures
- Use proper subdirectories for all new content
- Document changes in appropriate `memory/` sections
- Maintain the simplified, focused interface

## Memory System
All project knowledge is organized in the `memory/` folder:
- Components documentation
- Feature specifications  
- Development notes
- Architecture details
- Quick references

For detailed information, see `memory/README.md`.

## 📍 Quick Start

**ALWAYS start by reading:**
1. `memory/README.md` - Overview of the entire memory system
2. `memory/index/quick_reference.md` - Critical information at a glance
3. `memory/user_interactions/current_session.md` - User preferences and context

## 📁 Memory System Structure

All project knowledge is organized in `memory/`:

```
memory/
├── README.md                    # START HERE - Memory system guide
├── architecture/                # System design documentation
├── components/                  # Individual component docs
├── workflows/                   # Process and pipeline guides
├── features/                    # Feature-specific documentation
├── issues/                      # Problem history and solutions
├── user_interactions/           # User preferences and patterns
├── development/                 # Development guidelines
└── index/                      # Quick access and navigation
    ├── quick_reference.md      # Essential info cheat sheet
    ├── cross_references.md     # Document relationships
    └── glossary.md             # Technical terms
```

## 🎯 Key Principles

1. **Memory First**: Always check the memory system before making changes
2. **User Context**: Respect documented user preferences and patterns
3. **Quality Focus**: Implement thorough, production-ready solutions
4. **Update Documentation**: Keep the memory system current with changes

## 🚀 Common Tasks

- **Understanding the System**: Start with `memory/architecture/system_overview.md`
- **UI Changes**: MUST read `memory/issues/ui_redesign_history.md` first
- **Export Issues**: See `memory/workflows/export_pipeline.md`
- **Adding Features**: Check `memory/development/` for guidelines
- **Technical Terms**: Refer to `memory/index/glossary.md`

## ⚠️ Critical Rules

1. **Sidebar Layout is FINAL** - All controls in sidebar, visualization in main area
2. **No Emoji in Matplotlib** - Causes export stalling
3. **Check Memory First** - Contains solutions to common problems
4. **Follow Established Patterns** - Use proven implementations from docs

## 💡 Remember

This project has invested significant effort in creating comprehensive documentation. Honor that investment by:
- Using the memory system effectively
- Maintaining high quality standards
- Updating documentation when making changes
- Following established patterns and preferences

**The memory system at `memory/` is your primary resource. Use it!** 