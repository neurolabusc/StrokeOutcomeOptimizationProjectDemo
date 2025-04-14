import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from sklearn.svm import SVR
import matplotlib.pyplot as plt
import os

# This script takes merged_artery_participants.tsv in as input
# By default, it attempts to use all columns of data to predict the final column of data (NIHSS)
# It trains the model using the remaining dataframe
# *Note, any extreme outliers with impossible scores (i.e. NIHSS actual or NIHSS predicted) are removed before plotting the figure.
# As a final step, the data is plotted.

#required: column name for response variable
rv = 'nihss'
#optional: remove specific features
columns_to_drop = []
# columns_to_drop = ['age_at_stroke', 'lesion_volume']
#optional: only preserve specific features (make sure to keep rv)
columns_to_keep = []
# columns_to_keep = ['age_at_stroke', 'lesion_volume', rv]
#required: name of spreadsheet to analyze
file_path = 'merged_artery_participants.tsv' # Replace with the path to your data file

# 1. Import data from Excel
# n.b. ignore the first column (particpant_id)
data = pd.read_csv(file_path, sep='\t', index_col=0)
# print(data)
# Remove rows where the rv has NaN values
data = data.dropna(subset=[rv])

if bool(columns_to_keep):
    data = data[columns_to_keep]
if bool(columns_to_drop):
    data = data.drop(columns_to_drop, axis=1)

# 3. Replace NaN with zeros and remove sparse columns
data = data.fillna(0)
data = data.loc[:, (data != 0).sum() > 0.1 * data.shape[0]]

# 4. Prepare data for leave-one-out
X = data.drop([rv], axis=1)
y = data[rv]
lesion_volume = data['lesion_volume']  # ensure this column is not dropped
scaled_sizes = 10 * ((lesion_volume - lesion_volume.min()) / (lesion_volume.max() - lesion_volume.min())) + 5  # scaling dot sizes

scaler = StandardScaler()

# 5. Initialize for leave-one-out cross-validation
loo = LeaveOneOut()
y_true, y_pred_nn, y_pred_svr = [], [], []

for train_index, test_index in loo.split(X):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model_nn = tf.keras.models.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model_nn.compile(optimizer='adam', loss='mean_squared_error')
    model_nn.fit(X_train, y_train, epochs=50, batch_size=10, verbose=0)
    pred_nn = model_nn.predict(X_test).flatten()

    model_svr = SVR(kernel='rbf')
    model_svr.fit(X_train, y_train)
    pred_svr = model_svr.predict(X_test)

    y_true.extend(y_test)
    y_pred_nn.extend(pred_nn)
    y_pred_svr.extend(pred_svr)

# Create a DataFrame with the data
results_df = pd.DataFrame({
    'Actual Values': y_true,
    'NN Predicted Values': y_pred_nn,
    'SVR Predicted Values': y_pred_svr,
    'Lesion Volume': data['lesion_volume'].values  # Add the lesion_volume column
})

#Clamp values such that they are forced to make sense (NIHSS > 30 or NIHSS > 0 do not make sense for this example)
results_df = results_df[(results_df['NN Predicted Values'] <= 30) & (results_df['NN Predicted Values'] >= 0) &
                        (results_df['SVR Predicted Values'] <= 30) & (results_df['SVR Predicted Values'] >= 0)]

correlation_nn, p_value_nn = pearsonr(y_true, y_pred_nn)
correlation_svr, p_value_svr = pearsonr(y_true, y_pred_svr)

print(f'Neural Network - Correlation (R): {correlation_nn}, p-value: {p_value_nn}')
print(f'SVR - Correlation (R): {correlation_svr}, p-value: {p_value_svr}')

# Define the directory to save the plot
output_directory = os.path.dirname(file_path)

# Save the DataFrame to a CSV file
results_file_path = os.path.join(output_directory, 'predictions_data.csv')
results_df.to_csv(results_file_path, index=False)

# Path to the CSV file
file_path = 'predictions_data.csv'

# Read the CSV file
data = pd.read_csv(file_path)

legend_size = 12

# Normalize 'lesionsize' to scale dot sizes. Adjust as needed.
min_size = 0.5  # Minimum size of the dot
max_size = 2.0  # Maximum size of the dot
sizes = (data['Lesion Volume'] / data['Lesion Volume'].max() * (max_size - min_size) + min_size) * 100  # Scaling factor for visibility

plt.figure(figsize=(12, 10))  # Set the figure size

# Plotting NN Predicted vs. Actual Values in green
plt.scatter(data['NN Predicted Values'], data['Actual Values'], color='green', s=sizes, label='NN Predicted', alpha=0.6)

# Plotting SVR Predicted vs. Actual Values in red
plt.scatter(data['SVR Predicted Values'], data['Actual Values'], color='red', s=sizes, label='SVR Predicted', alpha=0.6)

# Adding diagonal line for perfect agreement
plt.plot([data['Actual Values'].min(), data['Actual Values'].max()], [data['Actual Values'].min(), data['Actual Values'].max()], 'k--', linewidth=2, label='Perfect Agreement')

# Adding titles and labels
plt.title('NIHSS Quotient Prediction', fontsize=18, fontweight='bold')
plt.xlabel('NIHSS Predicted Values', fontsize=16, fontweight='bold')
plt.ylabel('NIHSS True Values', fontsize=16, fontweight='bold')

# Significantly increase font size of the legend
plt.legend(loc='lower right', fontsize=legend_size, title='Model Predictions', title_fontsize=legend_size, prop={'size': legend_size}, frameon=False)

# Set tick labels larger and bold
plt.xticks(fontsize=14, fontweight='bold')
plt.yticks(fontsize=14, fontweight='bold')

plt.grid(False)  # Optional: Adds a grid
plt.show()  # Display the plot
