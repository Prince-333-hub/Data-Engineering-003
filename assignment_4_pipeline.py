import os
import pandas as pd


source_folder = r"C:\Users\jyoti\OneDrive\Desktop\Data_Engineering_Project\source_folder"
source_file = os.path.join(source_folder, "Sample - Superstore.csv")

destination_folder = r"C:\Users\jyoti\OneDrive\Desktop\Data_Engineering_Project\destination_folder"
destination_file = os.path.join(destination_folder, "Superstore_copied.csv")

print("--- Starting Pipeline Execution ---")

if os.path.exists(source_file):
    print(f"[SUCCESS] Source file validation passed.")
    print(f"Target File: {source_file}")
    print(f"File Size: {os.path.getsize(source_file)} bytes\n")
    

    print("Executing Copy Data activity...")
    try:

        df = pd.read_csv(source_file, encoding='latin1')
        
                os.makedirs(destination_folder, exist_ok=True)
        

        df.to_csv(destination_file, index=False)
        
        print("\n[SUCCESS] Pipeline Execution Completed Successfully!")
        print(f"Data successfully copied to: {destination_file}")
        
    except Exception as e:
        print(f"\n[ERROR] Failed during copy activity: {e}")
else:
    print(f"[ERROR] Source file not found!")
    print(f"Expected to find it here: {source_file}")
