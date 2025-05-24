# ⚙️ User Preferences & Settings Guide

## 🎯 Overview
The Streamlit interface now includes comprehensive user preferences that **persist across sessions**. All your favorite settings are saved automatically and will be remembered the next time you use the app!

## 📍 Where to Find Settings
Look for the **"⚙️ User Preferences & Settings"** expandable section at the top of the main page, right below the title.

## 🎬 Animation Preferences

### Default Settings You Can Configure:

#### **Default FPS** (1-30)
- **What it does**: Sets the default animation speed when you load animations
- **Default**: 15 FPS (increased from 10 for smoother playback)
- **Your setting**: Whatever you last saved

#### **Default View Mode**
- **Options**: Thumbnail Grid, Timeline Strip, Single Frame
- **What it does**: Automatically sets your preferred way to view animations
- **Your setting**: Remembers your choice (e.g., always start with Thumbnail Grid)

#### **Default Max Thumbnails** (8-32)
- **What it does**: Sets how many thumbnail previews to show in grid mode
- **Default**: 16 thumbnails
- **Your setting**: Maybe you prefer 24 for more overview, or 12 for faster loading

#### **Default Grid Columns** (3-6)
- **What it does**: Sets the grid layout for thumbnail view
- **Default**: 4 columns
- **Your setting**: Perhaps 6 columns for more compact view, or 3 for larger previews

#### **Default Strip Frames** (6-20)  
- **What it does**: Sets how many frames to show in timeline strip mode
- **Default**: 12 frames
- **Your setting**: Maybe 20 for more detail, or 8 for cleaner view

#### **Auto-launch Desktop Viewer**
- **What it does**: Automatically opens the 3D desktop viewer when you load animations
- **Default**: Off (you click the button manually)
- **Your setting**: Enable if you always want the 3D viewer to open automatically

## 🎲 Generation Preferences

#### **Default Shape**
- **Options**: Sphere, Torus, Helix, Cube, Random
- **Default**: Sphere
- **Your setting**: If you always work with Torus animations, set it as default

#### **Default Point Count** (100-10,000)
- **Default**: 3,000 points (increased from 2,000)
- **Your setting**: Maybe 5,000 for high-detail work, or 1,000 for quick testing

#### **Auto-generate Preview**
- **What it does**: Automatically shows the matplotlib preview when generating
- **Default**: On
- **Your setting**: Turn off if you only care about the desktop viewer

#### **Show Advanced Controls**
- **What it does**: Shows additional options and fine-tuning controls
- **Default**: Off (clean interface)
- **Your setting**: Enable if you're a power user who wants all options

## 🎥 Export Preferences

#### **Default Video Quality**
- **Options**: Low, Medium, High, Ultra
- **Default**: High
- **Your setting**: Ultra for publication quality, or Medium for faster exports

#### **Auto-download Exports**
- **What it does**: Automatically triggers download when video export completes
- **Default**: On
- **Your setting**: Turn off if you prefer manual download control

## 💾 How Preferences Work

### Saving Your Settings
1. **Adjust any setting** in the preferences panel
2. **Click "💾 Save Preferences"** 
3. **Settings are saved** to `user_preferences.json` in your project directory
4. **Success message** confirms your settings are saved

### Automatic Loading
- **Next time you start** the app, all your preferences are loaded automatically
- **Default values** use your saved preferences instead of app defaults
- **Session state** is initialized with your preferences

### Resetting to Defaults
- **Click "🔄 Reset to Defaults"** to restore original app settings
- **Useful** if you want to start fresh or fix any setting issues

## 🚀 Practical Usage Examples

### Example 1: Animation Power User
**Your workflow**: You always work with 48-frame torus animations, prefer 6-column grids, and want the desktop viewer to launch automatically.

**Settings to configure**:
- Default View Mode: "Thumbnail Grid"
- Default Max Thumbnails: 24
- Default Grid Columns: 6
- Auto-launch Desktop Viewer: ✅ Enabled
- Default Shape: "Torus"

### Example 2: Quick Tester
**Your workflow**: You generate lots of small test point clouds and don't need high-quality exports.

**Settings to configure**:
- Default Point Count: 1,000
- Default Video Quality: "Medium"
- Auto-generate Preview: ❌ Disabled
- Show Advanced Controls: ❌ Disabled

### Example 3: High-Quality Producer  
**Your workflow**: You create detailed animations for presentations with maximum quality.

**Settings to configure**:
- Default Point Count: 8,000
- Default Video Quality: "Ultra"
- Default Max Thumbnails: 32
- Auto-download Exports: ✅ Enabled

## 📂 Technical Details

### Storage Location
- **File**: `user_preferences.json` in your project root
- **Format**: Human-readable JSON
- **Backup**: You can copy this file to save your settings

### Session Persistence
- **Current session**: Changes take effect immediately
- **Future sessions**: Saved preferences load automatically on app start
- **Multiple users**: Each user can have their own preferences file

### Compatibility
- **Backwards compatible**: Old sessions work fine
- **Forward compatible**: New preference options added seamlessly
- **Error handling**: If preferences file is corrupted, defaults are used

## 🎯 Benefits

### Time Saving
- **No more repetitive setup** - your preferred settings are always ready
- **Faster workflow** - skip the configuration step
- **Consistent experience** - same setup every time

### Personalization  
- **Tailored to your needs** - everyone has different preferences
- **Workflow optimization** - settings match your typical usage
- **Professional efficiency** - spend time on work, not setup

### Team Collaboration
- **Shareable settings** - copy preferences.json to team members
- **Standardized workflows** - everyone can use the same optimal settings
- **Training efficiency** - new users get proven configurations

## 💡 Pro Tips

1. **Start with defaults** and gradually customize as you discover your preferences
2. **Save settings frequently** especially when you find a configuration you like
3. **Backup your preferences file** if you've spent time perfecting your setup
4. **Try different configurations** for different types of projects
5. **Use auto-launch desktop viewer** if you always want the 3D view

Your settings are now part of your workflow - the app adapts to you! 🎉 