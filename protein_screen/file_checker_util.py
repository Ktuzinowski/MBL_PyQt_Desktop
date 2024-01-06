import re


def check_file_for_new_image(filename):
    # Regular expression to match file extensions .tif, .tiff, .jpg, or .png
    pattern = r"1\.(tif|tiff|jpg|png)$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return True
    else:
        return False


def check_file_for_tif_image(filename):
    # Regular expression to match .tif file
    pattern = r"\.(tif|tiff)$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return True
    else:
        return False


def check_file_for_excel(filename):
    # Regular expression to match file extensions .xlsx
    pattern = r"\.(xlsx)$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return True
    else:
        return False


def check_file_extension(filename):
    # Regular expression to match file extensions .tif, .tiff, .jpg, or .png
    pattern = r"\.(tif|tiff|jpg|png)$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        return True
    else:
        return False
