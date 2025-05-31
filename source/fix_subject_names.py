"""
One-time script to fix subject names in CSV files.
Updates the Subject Name column to match the experiment folder name.
"""

import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
import os

def fix_subject_names():
    # Get the root data directory
    root_dir = Path("data/read")
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_dir = root_dir.parent / f"backup_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    
    print(f"📁 Created backup directory: {backup_dir}")
    
    # Track statistics
    total_files = 0
    modified_files = 0
    errors = []
    
    # Process each experiment directory
    for exp_dir in root_dir.glob("e*"):
        if not exp_dir.is_dir():
            continue
            
        # Get the subject name from directory (e.g., "e1", "e2", etc.)
        subject_name = exp_dir.name
        print(f"\n🔍 Processing {subject_name}...")
        
        # Create corresponding backup directory
        exp_backup_dir = backup_dir / subject_name
        exp_backup_dir.mkdir(exist_ok=True)
        
        # Process each CSV file in the experiment directory
        for csv_file in exp_dir.glob("*.csv"):
            total_files += 1
            print(f"  📄 Processing {csv_file.name}")
            
            try:
                # Create backup
                shutil.copy2(csv_file, exp_backup_dir / csv_file.name)
                
                # Read CSV
                df = pd.read_csv(csv_file)
                
                # Check if Subject Name column exists
                if 'Subject Name' in df.columns:
                    # Check if any values are different from subject_name
                    if not all(df['Subject Name'] == subject_name):
                        df['Subject Name'] = subject_name
                        df.to_csv(csv_file, index=False)
                        modified_files += 1
                        print(f"    ✅ Updated subject name to {subject_name}")
                    else:
                        print(f"    ℹ️ Subject name already correct")
                else:
                    print(f"    ⚠️ No 'Subject Name' column found")
                    errors.append(f"{csv_file}: No 'Subject Name' column")
                    
            except Exception as e:
                error_msg = f"{csv_file}: {str(e)}"
                print(f"    ❌ Error: {error_msg}")
                errors.append(error_msg)
    
    # Print summary
    print("\n📊 Summary:")
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {modified_files}")
    print(f"Errors encountered: {len(errors)}")
    
    if errors:
        print("\n⚠️ Errors:")
        for error in errors:
            print(f"- {error}")
    
    print(f"\n💾 Backup saved to: {backup_dir}")
    print("✨ Done!")

if __name__ == "__main__":
    fix_subject_names() 