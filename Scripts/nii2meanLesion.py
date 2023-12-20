#this script with assistance from ChatGPT3.5 20231204
# the function is to create a mean of all the normalized images
#  python nii2meanLesion.py

import os
import nibabel as nib
import numpy as np
import fnmatch

def create_mean_image(folder_path, output_path):
    # Ensure the output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Get a list of all NIfTI files in the folder
    nifti_files = [f for f in os.listdir(folder_path) if fnmatch.fnmatch(f, 'bwsrsub-*_lesion.nii.gz')]

    if not nifti_files:
        print("No NIfTI files found in the specified folder.")
        return

    # Load the first NIfTI image to get dimensions
    first_nifti = nib.load(os.path.join(folder_path, nifti_files[0]))
    mean_data = np.zeros_like(first_nifti.get_fdata(), dtype=np.float32)

    # Accumulate data from all images
    for nifti_file in nifti_files:
        nifti_path = os.path.join(folder_path, nifti_file)
        nifti_data = nib.load(nifti_path).get_fdata()
        mean_data += nifti_data

    # Calculate the mean
    mean_data /= len(nifti_files)

    # Create a new NIfTI image with the mean data
    mean_nifti = nib.Nifti1Image(mean_data, first_nifti.affine, first_nifti.header)

    # Save the mean NIfTI image
    nib.save(mean_nifti, os.path.join(output_path, f"lesion_mean_{len(nifti_files)}.nii.gz"))

    print(f"Mean of {len(nifti_files)} images saved to: {output_path}")

if __name__ == "__main__":
    input_path = "../NIfTI"  # folder path containing NIfTI images
    output_path = "../NIfTI"  # desired output path

    create_mean_image(input_path, output_path)
