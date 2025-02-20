import os
import nibabel as nib
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, mannwhitneyu

# Load participant data
participants_df = pd.read_csv("participants.tsv", sep="\t")

# Function to calculate lesion volume (in cc)
def calculate_lesion_volume(nifti_path):
    img = nib.load(nifti_path)
    data = img.get_fdata()
    voxel_volume = np.prod(img.header.get_zooms()) / 1000  # Convert mm^3 to cc
    lesion_volume = np.sum(data > 0) * voxel_volume
    return lesion_volume

# Collect lesion volumes by gender
male_volumes = []
female_volumes = []

for _, row in participants_df.iterrows():
    participant_id = row['participant_id']
    gender = row['sex']
    nifti_path = f"../NIfTI/bwsr{participant_id}_lesion.nii.gz"

    if os.path.exists(nifti_path):
        volume = calculate_lesion_volume(nifti_path)
        if gender == 'M':
            male_volumes.append(volume)
        elif gender == 'F':
            female_volumes.append(volume)

# Convert lists to numpy arrays
male_volumes = np.array(male_volumes)
female_volumes = np.array(female_volumes)

# Descriptive statistics
male_mean, male_std, male_median, male_iqr = (np.mean(male_volumes), np.std(male_volumes),
                                              np.median(male_volumes), np.percentile(male_volumes, [25, 75]))
female_mean, female_std, female_median, female_iqr = (np.mean(female_volumes), np.std(female_volumes),
                                                      np.median(female_volumes), np.percentile(female_volumes, [25, 75]))

# One-sided t-test (mean)
t_stat, p_value_t = ttest_ind(male_volumes, female_volumes, alternative='greater')

# One-sided Mann-Whitney U test (median)
mw_stat, p_value_mw = mannwhitneyu(male_volumes, female_volumes, alternative='greater')

# Output results
print("Lesion Volume Analysis by Gender")
print("=================================")
print(f"Males (n = {len(male_volumes)}): Mean = {male_mean:.2f} cc, Std Dev = {male_std:.2f} cc, Median = {male_median:.2f} cc, IQR = {male_iqr[0]:.2f}-{male_iqr[1]:.2f} cc")
print(f"Females (n = {len(female_volumes)}): Mean = {female_mean:.2f} cc, Std Dev = {female_std:.2f} cc, Median = {female_median:.2f} cc, IQR = {female_iqr[0]:.2f}-{female_iqr[1]:.2f} cc")
print("\nStatistical Tests (One-sided)")
print("------------------------------")
print(f"T-test (Mean Comparison): t = {t_stat:.2f}, p = {p_value_t:.4f}")
print(f"Mann-Whitney U test (Median Comparison): U = {mw_stat:.2f}, p = {p_value_mw:.4f}")
