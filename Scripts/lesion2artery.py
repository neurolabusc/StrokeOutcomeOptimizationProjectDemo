import nibabel as nib
import numpy as np
from scipy import ndimage
import sys
import csv
import os
import glob

def count_nonzero_voxels_in_atlas(atlas_data, image_path):
    # Load the second NIfTI image
    image_img = nib.load(image_path)
    image_data = image_img.get_fdata()

    # Extract connected components for the atlas
    labeled_atlas, num_regions = ndimage.label(atlas_data)
    # Initialize a dictionary to store non-zero voxel counts for each region
    region_counts = {}

    # Iterate through each region of the atlas
    for region_label in range(1, atlas_data.max()+1):
        # Create a binary mask for the current region in the atlas
        region_mask = atlas_data == region_label

        # Apply the mask to the second NIfTI image
        region_data = np.multiply(region_mask, image_data)

        # Count non-zero voxels for the current region
        nonzero_voxels = np.count_nonzero(region_data)
        #if nonzero_voxels < 1:
        #    continue
        atlas_nvox = np.count_nonzero(atlas_data == region_label)
        
        # Store the result in the dictionary
        region_counts[region_label] = nonzero_voxels/atlas_nvox

    total = np.count_nonzero(image_data)
    return [region_counts, total]


def load_and_create_lookup_table(file_path):
    # Initialize an empty dictionary as the lookup table
    lookup_table = {}

    # Open the file and read its contents
    with open(file_path, 'r') as file:
        # Iterate through each line in the file
        for line in file:
            # Split the line using the "|" symbol as the delimiter
            columns = line.strip().split('|')

            # Extract the key (index) and value (string) from the columns
            key = int(columns[0].strip())
            value = columns[1].strip()

            # Store the key-value pair in the lookup table
            lookup_table[key] = str(key)+'_'+value
    return lookup_table

def find_matching_files(folder_path, pattern):
    # Create the file pattern using the provided filter
    file_pattern = os.path.join(folder_path, pattern)
    
    # Use glob to find matching files
    matching_files = sorted(glob.glob(file_pattern))
    return matching_files

def remove_prefix(input_string, prefix):
    # Check if the input string starts with the specified prefix
    if input_string.startswith(prefix):
        # Remove the prefix by slicing the string
        result = input_string[len(prefix):]
        return result
    else:
        # If the prefix is not present, return the original string
        return input_string

if __name__ == "__main__":
    # Specify the path to the NIfTI atlas
    folder_path = "../NIfTI/"
    atlas_path = folder_path + "ArterialAtlas136.nii.gz"
    atlas_text = folder_path + "ArterialAtlas136.txt"
    atlas_labels = load_and_create_lookup_table(atlas_text)
    # Load the atlas
    atlas_img = nib.load(atlas_path)
    atlas_data = atlas_img.get_fdata()
    atlas_data = atlas_data.astype(int)
    # Specify the path to the second NIfTI image
    prefix = 'bwsr'
    file_pattern = prefix + '*_lesion.nii.gz'

    #for region in range(1, atlas_data.max()):
    #    if region in atlas_labels:
    #        print(f"{atlas_labels[region]}: {counts[region]}/{atlas_nvox[region]} non-zero voxels")
    output_file = "artery.tsv"
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(output_file, 'a') as output:
        output.write("participant_id\t")
        output.write("lesion_volume\t")
        output.write("\t".join(f"{atlas_labels[region]}" for region in range(1, atlas_data.max()+1)))
        output.write("\n")

    matching_files = find_matching_files(folder_path, file_pattern)
    print(f"{len(matching_files)} files match {file_pattern}" )
    for image_path in matching_files:
            # Count non-zero voxels for each region in the atlas
            [counts, total] = count_nonzero_voxels_in_atlas(atlas_data, image_path)
            with open(output_file, 'a') as output:
                # Write header to the output file
                subj = os.path.basename(image_path)
                parts = subj.split('_')
                subj = remove_prefix(parts[0], prefix)
                output.write(subj+"\t")
                output.write(str(total)+"\t")
                output.write("\t".join(f"{counts[region]}" for region in range(1, atlas_data.max()+1)))
                output.write("\n")
