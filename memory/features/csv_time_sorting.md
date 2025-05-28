# CSV Time-Based Sorting Feature

## Overview
Automatic time-based sorting for facial landmark CSV files during import to ensure frames are processed in chronological order.

## Problem Solved
Many facial landmark CSV files have frames that are not sorted by time, which can cause:
- Incorrect animation sequences
- Jumpy or erratic playback
- Confusion when analyzing temporal patterns

## Implementation
Located in: `source/streamlit_interface.py` - `load_and_preview_csv()` method

### Features:
1. **Automatic Detection**: Checks if 'Time (s)' column exists
2. **Smart Sorting**: Sorts data by time while preserving all columns
3. **User Notification**: Informs user when data has been sorted
4. **Time Range Display**: Shows min/max time and total duration
5. **Preview Update**: Shows "sorted by time" in preview header

### Code:
```python
# Check if Time (s) column exists and sort by it
if 'Time (s)' in df.columns:
    original_order = df.index.tolist()
    df = df.sort_values('Time (s)').reset_index(drop=True)
    
    # Check if sorting changed the order
    if df.index.tolist() != original_order:
        st.info("📊 Data has been automatically sorted by Time (s) column")
```

## User Experience
- Transparent to user - happens automatically
- Clear notification when sorting occurs
- Time range info helps verify data integrity
- No manual intervention required

## Benefits
- Ensures correct temporal order for animations
- Prevents frame jumping issues
- Makes microexpression analysis more accurate
- Improves overall data quality 