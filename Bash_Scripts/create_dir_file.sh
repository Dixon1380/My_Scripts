#!/bin/bash
# Use this code to create a folder or file on the fly. 
read -p "Enter 'file' to create a new file or 'directory' to create a new directory: " choice

if [[ "$choice" == "file" ]]; then
    read -p "Enter the name of the file you want to create: " filename
    touch "$filename"
    echo "File '$filename' created successfully."
elif [[ "$choice" == "directory" ]]; then
    read -p "Enter the name of the directory you want to create: " dirname
    mkdir "$dirname"
    echo "Directory '$dirname' created successfully."
else
    echo "Invalid choice. Please enter 'file' or 'directory'."
    exit 1
fi
