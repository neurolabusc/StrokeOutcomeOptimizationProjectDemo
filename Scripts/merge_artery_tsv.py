import pandas as pd

def concatenate_and_discard(file1_path, file2_path, output_path):
    # Read the two CSV files into DataFrames
    df1 = pd.read_csv(file1_path, sep='\t')
    df2 = pd.read_csv(file2_path, sep='\t')

    # Merge the two DataFrames based on the first column (assumed to be the names)
    merged_df = pd.merge(df1, df2, on=df1.columns[0], how='inner')

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv(output_path, sep='\t', index=False)

if __name__ == "__main__":
    file1_path = "artery_cleaned.tsv"
    file2_path = "participants_cleaned.tsv"
    output_path = "merged_artery_participants.tsv"

    concatenate_and_discard(file1_path, file2_path, output_path)
