#!/bin/usr/env python3

"""This script uses the OS module to create directories from the command line automatically."""

import os 

def get_current_directory():
    return os.getcwd()


# Default Key Directory locations...you can custom this dictionary if you prefer.
HOME_USERS_DEFAULT_DIRECTORIES = {
    'CWD': get_current_directory(),
    'Desktop': os.path.join('/Users',os.getenv('USER'), 'Desktop'), 
    'Documents': os.path.join('/Users',os.getenv('USER'), 'Documents'),
    'Downloads': os.path.join('/Users',os.getenv('USER'), 'Download'),
    'Pictures': os.path.join('/Users',os.getenv('USER'), 'Pictures'),
    'Music': os.path.join('/Users',os.getenv('USER'), 'Music'),
    'Movies': os.path.join('/Users',os.getenv('USER'), 'Movies')
}

# Creating one directory only
def create_directory(path):
    """Creates a directory with the name of your choice in a given path"""
    dir_name = input("What would like to name the directory?: ")
    file_path = os.path.join(path, dir_name)
    if os.path.exists(file_path):
        raise OSError("Error: Cannot create directory. Directory already exists.")
    elif not os.path.exists(file_path) and os.path.isdir(file_path):
        raise OSError("Error: Cannot create directory. Directory name already exists.")
    else:
        try:
            os.mkdir(file_path)
            print("Directory has been created successfully! ")
            print(f'Directory location is: {file_path}')
        except OSError as error:
            print(error)


# Creating multiple directories at once
def make_sub():
    """Returns a boolean based on whether the directories specified will be subdirectories for the given path
        Example:
            Return True: All directories created will be subdirectories in the given path
            Return False: All directories created will not be subdirectories in the given path
    """
    sub = input("Do you want these directories to be subdirectories?(y/n): ")
    if sub.lower() == 'y':
        sub = True
    elif sub.lower() == 'n':
        sub = False
    return sub

def create_directories(path, sub=False):
    "Creates directories with the names of your choice in a given path. Also create subdirectories"
    def dir_name_generator():
        """Specifies how many directories you want and their names and returns a tuple of those directories"""
        dir_quantity = int(input("How many directories do you want?: "))
        dir_list = []
        for dir_name in range(1, dir_quantity+1):
            dir_name = input("What would like to name the directory: ")
            dir_list.append(dir_name)
        return dir_list
    dir_list = dir_name_generator()
    # determines whether to create directories as subdirectories or not. See 'make_sub' function for details
    if sub == False:
        for dir in dir_list:
            file_path = os.path.join(path, dir)
            if os.path.isdir(file_path):
                try:
                    os.mkdir(file_path)
                except OSError:
                    raise("Error: Cannot create directory!")
    else:
        file_path = path
        for dir in dir_list:
            file_path += os.path.join('/', dir)
        print(file_path)
        if os.path.exists(file_path):
            raise OSError("Error: Cannot create directory! This path already exists or directories in the path are already created.")
        try:
            os.makedirs(file_path)
        except OSError as error:
            print(error)
    print("All directores were created successfully!")
    print(f'Directory location is: {path}')


def print_default_directories():
    print("List of directories to choose:")
    print("Select the key you want your current Directory to be.")
    for key, directory in HOME_USERS_DEFAULT_DIRECTORIES.items():
        print(f"{key} -> {directory}")


def main():
    path = get_current_directory()
    print(f"Current Directory is: {path}")
    choice = input("Do you want to use the current directory?(y/n): ")
    if choice.lower() == 'n':
        path = ''
        print_default_directories()
        default_dir_key = input("Where would you like your current directory to be?: ")
        if default_dir_key in HOME_USERS_DEFAULT_DIRECTORIES.keys():
            path = HOME_USERS_DEFAULT_DIRECTORIES[default_dir_key]
        else:
            raise KeyError(f"{default_dir_key} does not exist as a default key. You must add it as a key")
        print(f"Your Current Directory is now set to: {path}\n\n")

    while True:
        try:
            choice = int(input("Choose an option:\n\n1) Create one directory\n\n2) Create multiple directories\n"))
            if choice == 1:
                create_directory(path)
                break
            elif choice == 2:
                create_directories(path, sub=make_sub())
                break
            else:
                print("Invalid input! Please enter 1 or 2.")
        except ValueError:
            print("Invalid input! Please enter a valid number.")

if __name__ == '__main__':
    main()
    
