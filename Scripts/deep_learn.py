#this script is almost like "deep_learn.py", however the scalar is run once for the whole dataset, which can leak a little from the hidden data.

#this script with assistance from ChatGPT
# a spreadsheet is where the first row is a header and first column is participant id
# the goal is to predict the column "wab_aq" based on imaging data
# we treat "age_at_stroke" as a predictor

import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from sklearn.svm import SVR

#required: column name for response variable
rv = 'nihss'
#optional: remove specific features
columns_to_drop = []
# columns_to_drop = ['age_at_stroke', 'lesion_volume']
#optional: only preserve specific features (make sure to keep rv)
columns_to_keep = []
# columns_to_keep = ['age', 'lesion_volume', rv]
#required: name of spreadsheet to analyze
file_path = "merged_artery_participants.tsv"  # Replace with the path to your data file

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
#optional normalize rv in range of 0..1, but based on whole sample leakage for leave-one-out
#y = (y - y.min()) / (y.max() - y.min())
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
 
# 5. Initialize for leave-one-out cross-validation
loo = LeaveOneOut()
y_true, y_pred_nn, y_pred_svr = [], [], []
 
for train_index, test_index in loo.split(X_scaled):
    X_train, X_test = X_scaled[train_index], X_scaled[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
 
    # Neural Network
    model_nn = tf.keras.models.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model_nn.compile(optimizer='adam', loss='mean_squared_error')
    model_nn.fit(X_train, y_train, epochs=50, batch_size=10, verbose=0)
    pred_nn = model_nn.predict(X_test).flatten()
 
    # SVR
    model_svr = SVR(kernel='rbf')
    model_svr.fit(X_train, y_train)
    pred_svr = model_svr.predict(X_test)
 
    # Collecting predictions
    y_true.extend(y_test)
    y_pred_nn.extend(pred_nn)
    y_pred_svr.extend(pred_svr)
 
# 6. Calculate the correlation (R) and p-value for both models
correlation_nn, p_value_nn = pearsonr(y_true, y_pred_nn)
correlation_svr, p_value_svr = pearsonr(y_true, y_pred_svr)
 
print(f'Neural Network - Correlation (R): {correlation_nn}, p-value: {p_value_nn}')
print(f'SVR - Correlation (R): {correlation_svr}, p-value: {p_value_svr}')