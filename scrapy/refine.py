import pandas as pd
import os
import chardet

# Function to detect file encoding
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # Read the first 10,000 bytes
    return result['encoding']

# Folder containing the CSV files
folder_path = 'D:\\University\\Python Programs\\CSV'

# Get all CSV files from the folder
all_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Create an empty list to store DataFrames
data_frames = []

for file in all_files:
    file_path = os.path.join(folder_path, file)
    
    # Detect encoding
    encoding = detect_encoding(file_path)
    print(f"Detected encoding for {file}: {encoding}")

    try:
        # Read the CSV file with detected encoding
        df = pd.read_csv(file_path, encoding=encoding)
        data_frames.append(df)
    except (UnicodeDecodeError, pd.errors.ParserError) as e:
        print(f"Error reading {file_path} with encoding {encoding}: {e}")

# Concatenate all DataFrames
if data_frames:
    combined_df = pd.concat(data_frames, ignore_index=True)
    # Save the combined CSV
    combined_df.to_csv('combined_file.csv', index=False)
else:
    print("No data frames to concatenate.")
