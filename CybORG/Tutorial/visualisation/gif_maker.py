# import cv2
import glob
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import sys
from math import log10


from results_parser import parse_results

##########################
# Constants
##########################
# # Image shades
known_shade = (1,0,0,0.5) # facecolor
unknown_shade = (0,0,1,0.5) # facecolor
access_none = 'b' # edgecolor
access_user = 'y' # edgecolor
access_priv = 'r' # edgecolor
server_shape_w = 65
server_shape_h = 85
host_shape_w = 62
host_shape_h = 62
legend_shape_w = 0
legend_shape_h = 0


def get_loc(hostname):
    """
    Get the location of the host on the image.

    param:
        hostname: string from API to specify host
    return:
        loc: tuple with position for graphic on specified host
    """
    locations = {
        "Enterprise0": (460, 55),
        "Enterprise1": (532, 55),
        "Enterprise2": (603, 55),
        "Op_Server0": (968, 55),
        "Op_Host0": (908, 315),
        "Op_Host1": (973, 315),
        "Op_Host2": (1035, 315),
        "User0": (0, 317),
        "User1": (67, 317),
        "User2": (135, 317),
        "User3": (204, 317),
        "User4": (273, 317),
        "Defender": (535, 315),
        "Legend_Known": (300, 35),
        "Legend_Unknown": (350, 35),
        "Legend_AccessNone": (300, 85),
        "Legend_AcsessUser": (350, 85),
        "Legend_AccessSystem": (400, 85),
    }
    if hostname in locations:
        loc = locations[hostname]
    else:
        loc = (0,0)
    return loc
    




def add_patch(hostname, known_state, access_state, scanned=False):
    """
    Add the necessary shape to the image

    param:
        hostname: string from API to specify host
        known_state: Boolean indicating if red agent knows the IP of the corresponding host
        access_state: ["None", "User", "Priveleged"] indicating red agent access to corresponding host
        scanned: Boolean indicating if blue agent previously scanned the corresponding host
    return:
        None, shape is added to the image.
    """
    label = ""
    # Translate variables to colors
    if known_state:
        facecolor_shade = known_shade
    else:
        facecolor_shade = unknown_shade
    if access_state == "None":
        edgecolor_shade = access_none
    elif access_state == "User":
        edgecolor_shade = access_user
    else: # access_state == "Privileged"
        edgecolor_shade = access_priv
        
    if "Enterprise" in hostname or "Server" in hostname:
        shape_w = server_shape_w
        shape_h = server_shape_h
    elif "Legend" in hostname:
        shape_w = legend_shape_w
        shape_h = legend_shape_h
        label = hostname.split("_")[1]
    else: # Host
        shape_w = host_shape_w
        shape_h = host_shape_h
    loc = get_loc(hostname)
    
    # Create a Rectangle patch
    rect = patches.Rectangle(loc, shape_w, shape_h, linewidth=3, 
                             edgecolor=edgecolor_shade, facecolor=facecolor_shade, label=label)
    # Add the patch to the Axes
    ax.add_patch(rect)

if __name__ == "__main__":
    # Grab logs
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = "logs_to_vis/results.txt" # CHANGE HERE
    results_json = parse_results(file_name)

    # delete all images in img folder
    for f in glob.glob("./img/img*.png"):
        os.remove(f)
        
    # Make images for each step
    for i in range(len(results_json)):
        img = results_json[i]
        base = Image.open('./img/figure1.png')
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(20, 8))
        # Display the image
        ax.imshow(base)

        for host in img["hosts"]:
            # Add the shape to cover host with specified information
            add_patch(host["hostname"], host["known"], host["access"], host["scanned"])
        # Add legend
        add_patch("Legend_Known", True, "None")
        add_patch("Legend_Unknown", False, "None")
        add_patch("Legend_AccessNone", True, "None")
        add_patch("Legend_AccessUser", True, "User")
        add_patch("Legend_AccessSystem", True, "Privileged")

        if i == 0:
            plt.title("Starting...")
        else:
            title = f"Step {i}:"
            # Add blue action, red action, reward, and episode reward to title if they are present in img
            if "blue_action" in img:
                title += f" Blue Action: {img['blue_action']}"
            if "red_action" in img:
                title += f" Red Action: {img['red_action']}"
            if "reward" in img:
                title += f" Reward: {img['reward']}"
            if "ep_reward" in img:
                title += f" Ep Reward: {img['ep_reward']}"
            plt.title(title)
        plt.axis('off')
        # show legend
        plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1))

        # the width of the step is the power of ten of the last step number (e.g. 3 for 1000, 4 for 10000, etc.)
        step_width = int(log10(len(results_json)) + 1)
        # format the step number to be of the width step_width and with trailing zeros
        format_str = f"./img/img%0{step_width}d.png"
        plt.savefig(format_str % i)
        # plt.show()
        plt.close()

    # Compile images into a gif
    # filepaths
    fp_in = "img/img*.png"
    fp_out = "img/results.gif" # "./img/" + file_name.lstrip("logs_to_vis/").rstrip(".txt") + ".gif"

    # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
    img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
    img.save(fp=fp_out, format='GIF', append_images=imgs,
             save_all=True, duration=1000, loop=1)

