# Facial Microexpression Analysis - Quick Reference

## 🚀 **Getting Started**

### **Workflow:**
1. **Import** → Select CSV file → Configure baseline mode
2. **Animation** → Adjust settings → Click "🎬 Create Animation" 
3. **View** → Click "🎮 Launch 3D Player"

### **Default Settings:**
- **First frame baseline**: Quick setup, uses first frame as reference
- **Kabsch-Umeyama**: Size normalization enabled by default
- **Movement heatmap**: Color coding by default

## 📁 **File Structure**
```
facemesh/
├── data/read/          # Place CSV files here
├── data/write/         # Animations created here
├── source/             # Application code
├── main.py             # Run this file
└── memory/             # Documentation
```

## 🎯 **Key Features**

### **Baseline Modes**
- **📌 First Frame** (Default): Uses first frame of current data as reference
- **📊 Custom Statistical**: Generate statistical baseline from separate CSV file

### **Alignment Options**
- **✅ Size Normalization** (Default): Removes subject size differences
- **📌 Kabsch Only**: Preserves size differences (legacy)

### **Color Modes**
- **Movement Heatmap**: Frame-to-frame displacement (microexpressions)
- **Statistical Deviation**: Compared to baseline (requires custom statistical baseline)
- **Single Color**: Simple blue coloring

## ⌨️ **3D Player Controls**
- **SPACE**: Play/pause animation
- **N/P**: Next/previous frame
- **C**: Toggle coordinate axes
- **Mouse**: Rotate, zoom, pan view

## 🛠️ **Quick Troubleshooting**
- **No CSV files**: Put files in `data/read/` directory
- **Import fails**: Check CSV has `feat_N_x/y/z` columns
- **Player won't launch**: Check Open3D installation
- **Custom baseline**: Generate statistical baseline in Import tab first

## 📊 **Technical Details**
- **Z-scaling**: 25x for better 3D visualization
- **Alignment**: Kabsch-Umeyama with scale factor constraints [0.01, 100.0]
- **Color normalization**: 95th percentile for movement intensity
- **Statistical baseline**: Mean ± std dev from multiple frames

## 🎯 **Best Practices**
- **Use first frame baseline** for quick analysis
- **Generate custom statistical baseline** for research applications
- **Enable size normalization** for cross-subject comparisons
- **Statistical deviation coloring** requires custom baseline

---

*For detailed documentation, see `memory/notes/` and `memory/features/` directories*