import pandas as pd

# restrict analysis to regions showing variability in 5% of sample
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6866937/
# “sufficient affection” as 5% of the whole sample

def filter_columns(input_file, output_file, threshold=0.05):
    # Read the tab-separated value file into a DataFrame
    df = pd.read_csv(input_file, sep='\t', index_col=0)

    # Calculate the percentage of non-zero values for each column
    non_zero_percentage = (df != 0).mean()

    # Filter columns where at least 5% of the values are non-zero
    selected_columns = non_zero_percentage[non_zero_percentage >= threshold].index
    filtered_df = df[selected_columns]

    # Write the filtered DataFrame to a new file
    filtered_df.to_csv(output_file, sep='\t')

if __name__ == "__main__":
    input_file = "artery.tsv"
    output_file = "artery_cleaned.tsv"

    filter_columns(input_file, output_file)
