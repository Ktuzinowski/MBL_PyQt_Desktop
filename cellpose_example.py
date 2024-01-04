import os
import shutil

import skimage
from cellpose import io
import random
import matplotlib.pyplot as plt
from cellpose import models, plot
from skimage.util import img_as_ubyte
import numpy as np

# Enter Directory Name containing the images
# Existing Masks Directory will be deleted
# (Does not read images in subfolders)

Input_Directory = "Research_Folder/sample_two_cycles/protein signal"
input_dir = os.path.join(Input_Directory, "")  # adds seperator to the end regardless if path has it or not

image_format = "tif"

save_dir = input_dir + "Masks/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
else:
    print("Existing Mask Directory found. Deleting it.")
    shutil.rmtree(save_dir)

# r=root, d=directories, f=files
files = []

for r, d, f in os.walk(input_dir):
    for fil in f:
        if image_format:
            if fil.endswith(image_format):
                files.append(os.path.join(r, fil))
            else:
                files.append(os.path.join(r, fil))
    break  # only read the root directory; can change this to include levels

if len(files) == 0:
    print("Number of images loaded: %d." % (len(files)))
    print("Cannot read image files. Check if folder has images")
else:
    print("Number of images loaded: %d." % (len(files)))

imgs = []  # store all images
# Read images
for f in files:
    im = io.imread(f)
    n_dim = len(im.shape)  # shape of image
    dim = im.shape  # dimensions of image
    channel = min(dim)  # channel will be dimension with min value usually
    channel_position = dim.index(channel)
    # if number of dimensions is 3 and channel is first index, swap channel to lsat index
    if n_dim == 3 and channel == 0:
        im = im.transpose(1, 2, 0)
        dim = im.shape
        print("Shape changed")
    print(dim)
    imgs.append(im)

nimg = len(imgs)
print("No of imagse loaded are: ", nimg)

print("Example Image:")

random_idx = random.choice(range(len(imgs)))
x = imgs[random_idx]
n_dim = len(x.shape)
file_name = os.path.basename(files[random_idx])
print(file_name + " has " + str(n_dim) + " dimensions/s")

if n_dim == 3:
    channel_image = x.shape[2]
    fig, axs = plt.subplots(1, channel_image, figsize=(12, 5))
    print("Image: %s" % file_name)
    for channel in range(channel_image):
        axs[channel].imshow(x[:, :, channel])
        axs[channel].set_title('Channel ' + str(channel + 1), size=5)
        axs[channel].axis('off')
    fig.tight_layout()
elif n_dim == 2:
    print("One Channel")
    plt.imshow(x)
    plt.show()
else:
    print("Channel number invalid or dimensions wrong. Image shae is: " + str(x.shape))

# RUN CELLPOSE

# CHOOSE A MODEL

# cyto2 was trained using user submissions
# 'cyto' and 'nuclei' are the original cellpose models for cytoplasm and nuclei.
# 'cyto2' was trained including user submissions
# 'tissuenet' was trained on the tissuenet data set, and
# 'livecell' was trained on the livecell data set

Model_Choice = "cyto"  # @param ["cyto", "nuclei", "cyto2", "tissuenet", "livecell"]
model_choice = Model_Choice

print("Using model ", model_choice)

# If the image has only one channel, leave it as 0
Channel_for_segmentation = 0  # @param[0,1,2,3]
segment_channel = int(Channel_for_segmentation)

# If you use cyto or tissuenet, tick if you have a nuclear channel
Use_nuclear_channel = False
Nuclear_channel = "3"
nuclear_channel = int(Nuclear_channel)

Diameter = 0
diameter = Diameter

# define CHANNELS to run segmentation on
# grayscale=0, R=1, G=2, B=3
# channels = [cytoplasm, nucleus]
# if NUCLEUS channel does not exist, set the second channel to 0
# channels = [0, 0]
# IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
# channels = [0,0] # IF YOU HAVE GRAYSCALE
# channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
# channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus

model_type = model_choice

# channels = [cytoplasm, nucleus]
if model_choice not in "Nucleus":
    if Use_nuclear_channel:
        channels = [segment_channel, nuclear_channel]
    else:
        channels = [segment_channel, 0]
else:  # nucleus
    channels = [segment_channel, 0]

# DEFINE CELLPOSE MODEL
# model_type='cyto' or model_type='nuclei'
model = models.CellposeModel(gpu=False, model_type=model_type)

# define CHANNELS to run segmentation on
# grayscale=0, R=1, G=2, B=3
# channels = [cytoplasm, nucleus]
# if NUCLEUS channel does not exist, set the second channel to 0
# channels = [0,0]
# IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
# channels = [0,0] # IF YOU HAVE GRAYSCALE
# channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
# channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus

# or if you have different types of channels in each image
# channels = [[2,3], [0,0], [0,0]]

# if diameter is set to None, the size of the cell is estimated on a per-image basis
# you can set the average cell 'diameter' in pixels yourself (recommended)
# diameter can be a list or a single number for all images
if diameter == 0:
    diameter = None
    print("Diameter is set to None. The size of the cells will be estimated on a per image basis")

# TEST CELLPOSE ON AN IMAGE
# YOU CAN TUNE THE PARAMETERS BELOW BASED ON YOUR IMAGE

# flow_threshold parameter is the maximum allowed error of the flows for each mask
# default is 4.0
# increase this threshold if cellpose is not returning as many masks as you'd expect
# decrease this threshold if cellpose is returning too many ill-shaped masks

# The Cell Probability Threshold determines probability that a detected object is a cell.
# The default is 0.0
# Decrease this threshold if cellpose is not returning as many masks as you'd expect
# or if masks are too small

# If you do not know diameter of the cells OR if cells are of varying diameters, enter 0 in the
# Diameter box and cellpose will automatically estimate the diameter

Image_Number = 1  # @param {type: "number"}
Image_Number -= 1  # indexing starts at zero
print(Image_Number)
Diameter = 0  # @param {type: "number"}
Flow_Threshold = 0.3  # @param {type:"slider", min:0.1, max:1.1, step:0.1}
flow_threshold = Flow_Threshold

Cell_Probability_Threshold = -1  # @param {type: "slider", min:-6, max:6, step:1}
cellprob_threshold = Cell_Probability_Threshold

diameter = Diameter
if diameter is 0:
    diameter = None
if Image_Number is -1:
    Image_Number = 0
    print("Image number is set to zero, opening first image.")
try:
    image = imgs[Image_Number]
except IndexError as i:
    print("Image number does not exist", i)
    print("Actual number of images in folder: ", len(imgs))
print("Image: %s" % os.path.splitext(os.path.basename(files[Image_Number]))[0])
img1 = imgs[1]

masks, flows, styles = model.eval(img1, diameter=diameter, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold, channels=channels)

# DISPLAY RESULTS
maski = masks
flowi = flows[0]

# convert to 8-bit if not so it can display properly in the graph
if img1.dtype != 'uint8':
    img1 = img_as_ubyte(img1)

fig = plt.figure(figsize=(24,8))
plot.show_segmentation(fig, img1, maski, flowi, channels=channels)
plt.tight_layout()
plt.show()

# USE CELLPOSE TO SEGMENT CELLS
# The values defined above will be used for segmentation
# The masks will be saved automatically
# Saving the flow image/s are optional. Tick if you want to save them.

# if you want to save the flow image/s:
Save_Flow = True
# Flow image will be resized when saved
save_flow = Save_Flow

print("Running segmentation on channel %s" % segment_channel)
print("Using the model: ", model_choice)
if diameter is None:
    print("Diameter will be estimated from the image")
else:
    print(f"Cellpose will use a diameter of {diameter}")

print(f"Using a flow threshold of: {flow_threshold} and a cell probability threshold of: {cellprob_threshold}")

# if too many images, it will lead to a memory error
# will evaluate on a per image basis
# masks, flows, styles = model.eval(imgs, diameter=diameter, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold, channels=channels)

# save images in folder with the diameter value used in cellpose
print("Segmentation Done. Saving Masks and flows now")
print("Save Directory is: ", save_dir)
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

if save_flow:
    print("Saving Flow")
    flows_save_dir = save_dir + "flows" + os.sep
    print("Save Directory for flows is: ", flows_save_dir)
    if not os.path.exists(flows_save_dir):
        os.mkdir(flows_save_dir)

for img_idx, img in enumerate(imgs):
    file_name = os.path.splitext(os.path.basename(files[img_idx]))[0]
    print("\nSegmenting: ", file_name)
    mask, flow, style = model.eval(img, diameter=diameter, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold, channels=channels)
    # save images in folder with the diameter value used in cellpose
    print("Segmentation complete. Saving masks and flows")
    # Output name for masks
    mask_output_name = save_dir + "MASK_" + file_name + ".tif"
    # Save mask as 16-bit in case this has to be used for detecting than 255 objects
    mask = mask.astype(np.uint16)
    # Save flow as 8-bit
    skimage.io.imsave(mask_output_name, mask, check_contrast=False)
    if save_flow:
        # output name for flows
        flow_output_name = flows_save_dir + "FLOWS_" + file_name + ".tif"
        # save as 8-bit
        flow_image = flow[0].astype(np.uint8)
        skimage.io.imsave(flow_output_name, flow_image, check_contrast=False)

# Save parameters used in Cellpose
parameters_file = save_dir + "Cellpose_parameters_used.txt"
outFile = open(parameters_file, "w")
outFile.write("CELLPOSE PARAMETERS\n")
outFile.write("Model: " + model_choice + "\n")
if diameter == 0:
    diameter = "Automatically estimated by cellpose"
outFile.write("Diameter: " + str(diameter) + "\n")
outFile.write("Flow Threshold: " + str(flow_threshold) + "\n")
outFile.write("Cell probability Threshold: " + str(cellprob_threshold) + "\n")
outFile.close()
print("\nSegmentation complete and files saved")

