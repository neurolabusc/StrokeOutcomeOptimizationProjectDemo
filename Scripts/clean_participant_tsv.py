import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def process_and_scale(input_path, output_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_path, sep='\t')

    # Extract the first (id), third (age), and eighth (nihss) columns
    selected_columns = df.iloc[:, [0, 2, 7]]
    #selected_columns = df.iloc[:, :]
    # Filter out rows with non-numeric or empty cells in the specified columns
    selected_columns = selected_columns[pd.to_numeric(selected_columns[selected_columns.columns[1]], errors='coerce').notna()]
    selected_columns = selected_columns[pd.to_numeric(selected_columns[selected_columns.columns[2]], errors='coerce').notna()]

    # Exclude the first column for scaling
    columns_to_scale = selected_columns.columns[1:]

    # Scale the selected columns to the range 0 to 1
    scaled_data = selected_columns[columns_to_scale]
    if (False):
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(selected_columns[columns_to_scale])

    # Create a DataFrame from the scaled data
    scaled_df = pd.DataFrame(scaled_data, columns=columns_to_scale)

    # Include the first column in the final output
    scaled_df = pd.concat([selected_columns[selected_columns.columns[0]], scaled_df], axis=1)

    # Save the processed and scaled DataFrame to a new CSV file
    scaled_df.to_csv(output_path, sep='\t', index=False)


if __name__ == "__main__":
    input_path = "participants.tsv"
    output_path = "participants_cleaned.tsv"
    process_and_scale(input_path, output_path)
