#!/usr/bin/env python

"""
This script is used for creating a qcow2 image and then mount it to a
nbd device in order to install LFS on it and then virtualize it with KVM or
whatever hypervisor you are using.
"""

import os
import shutil
import subprocess
import shlex


# Image configuration
image_name = "LFS"
image_format = "qcow2"
fs_type = "ext4"
swap = True
image_size = "10G"
image_path = "/home/"+ os.getlogin() + "/" + image_name + "." + image_format

# Directory configuration
installation_path = "/mnt/LFS"
sources = "/mnt/LFS/sources"

# This function allow to check if the nbd kernel module is loaded; if not, it
# will load it. It requires sudo permissions.
def check_nbd():
    print("Checking nbd module...")
    if os.access("/dev/nbd0", os.F_OK):
        print("nbd kernel module already loaded.")

    else:
        print("nbd kernel module not loaded. Loading...")
        subprocess.check_output(shlex.split('sudo modprobe nbd max_part=16'))
        if os.access("/dev/nbd0", os.F_OK):
            print("nbd module: OK")

# Checks if the build dir structure is correclty set
def check_dirs():

    if os.access(installation_path, os.F_OK):
        print("Build dir is correctly set.")
    else:
        print("Build dir does not exist, creating it...")
        subprocess.check_output(shlex.split('sudo mkdir ' + installation_path))
        check_dirs()

def build_image():
    print("Building image...")

    # Image creation process
    subprocess.check_output(shlex.split('qemu-img create -f ' + image_format +
        ' ' + image_path + ' ' + image_size))
    if os.access(image_path, os.F_OK):
        print("Image successfully created.")


    # linking the image with the nbd device
    print("nbd-connecting the image...")
    subprocess.check_call(shlex.split('sudo qemu-nbd -c /dev/nbd0 '+ image_path))

    # Setting a partition table for the image
    print("Partitioning...")
    os.system('{\n' \
    'echo ",512,82"\n' \
    'echo ";"\n' \
    '} | sudo sfdisk /dev/nbd0 -D -uM\n')

    # Formatting the image, swap and ext3
    print("Formating image")
    os.system("sudo mkswap /dev/nbd0p1; sudo mkfs.ext3 /dev/nbd0p2 " + \
    "; sudo mount /dev/nbd0p2 "+ installation_path)
    print("Mounting image to " + installation_path + ".")

# Calling functions
check_nbd()
check_dirs()
build_image()
