# Agentic Memory Architecture for Facemesh Codebase

## Overview

This document establishes the memory architecture for AI agents working with the facemesh codebase. It follows best practices from modern agentic systems to ensure persistent, contextual, and efficient knowledge management.

## Memory Types Implemented

### 1. **Short-Term Memory (Working Memory)**
- **Purpose**: Maintain current conversation context and immediate task state
- **Scope**: Current session interactions, recent code changes, active debugging
- **Storage**: Session state, conversation history, recent file modifications
- **Retention**: Until session ends or context window limits

### 2. **Long-Term Memory (Semantic Memory)**
- **Purpose**: Persistent knowledge about codebase architecture, patterns, and solutions
- **Scope**: Code structure, design decisions, recurring issues, successful solutions
- **Storage**: Markdown files with structured metadata and cross-references
- **Retention**: Permanent, with periodic updates

### 3. **Procedural Memory**
- **Purpose**: How-to knowledge for common tasks and workflows
- **Scope**: Setup procedures, debugging workflows, deployment steps
- **Storage**: Structured guides with step-by-step instructions
- **Retention**: Permanent, version-controlled

### 4. **Episodic Memory**
- **Purpose**: Record of specific events, issues, and their resolutions
- **Scope**: Bug fixes, feature implementations, user interactions
- **Storage**: Timestamped entries with context and outcomes
- **Retention**: Historical record with search capability

## Memory Organization Structure

```
memory/
├── architecture/           # High-level system understanding
├── components/            # Individual component knowledge
├── workflows/             # Process and procedure memory
├── issues/               # Problem-solution pairs
├── user_interactions/    # Session and user-specific memory
└── index/               # Cross-references and search aids
```

## Core Principles

### 1. **Contextual Persistence**
- Each memory entry includes context: when, why, what changed
- Cross-references between related memories
- Version awareness for code changes

### 2. **Hierarchical Organization**
- High-level architectural knowledge → Specific component details
- Abstract patterns → Concrete implementations
- General principles → Specific examples

### 3. **Searchable and Retrievable**
- Standardized metadata tags
- Cross-reference links
- Index files for quick lookup

### 4. **Incrementally Updatable**
- New information augments existing knowledge
- Deprecated information marked but preserved
- Change history maintained

## Implementation Standards

### Memory Entry Format
```markdown
# [Title]
**Type**: [Short-term/Long-term/Procedural/Episodic]
**Context**: [Project area, date, trigger]
**Tags**: [searchable, keywords]
**Related**: [links to related memories]

## Content
[Structured information]

## Metadata
- Created: [timestamp]
- Updated: [timestamp]
- Confidence: [high/medium/low]
- Source: [conversation/code/documentation]
```

### Cross-Reference System
- Use `[[memory-id]]` for internal links
- Maintain bidirectional references
- Regular index updates

### Search and Retrieval
- Tag-based categorization
- Full-text search capability
- Hierarchical browsing
- Temporal filtering

## Current Codebase Context

### Project: Facemesh Point Cloud Visualization
- **Primary Function**: Streamlit interface for point cloud animations and MP4 export
- **Technology Stack**: Python, Streamlit, Open3D, matplotlib, OpenCV
- **Architecture**: Web UI + Desktop viewer integration
- **Current Status**: Fully functional with recent UI improvements

### Key Components Identified
1. **Streamlit Interface** (`streamlit_open3d_launcher.py`)
2. **Desktop Viewer Integration** (Open3D backend)
3. **Animation System** (PLY file sequences)
4. **Export Pipeline** (MP4 video generation)
5. **Memory Management** (Session state, notifications)

## Evolution Log

### Session 1: Initial Assessment
- **Date**: 2025-01-24
- **Context**: User requested memory system implementation
- **Status**: Memory architecture established
- **Next**: Populate component-specific memories

---

*This document serves as the foundation for all agentic memory operations in this codebase. All AI agents should reference and update this architecture as they learn about the system.* 