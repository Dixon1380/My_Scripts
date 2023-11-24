#!/bin/bash

# Prompt for user input
read -p "Enter your Git username: " username
read -p "Enter your Git email: " email

# Set global configuration
git config --global user.name "$username"
git config --global user.email "$email"

# Optional: set other configurations
# git config --global core.editor "vim" # Set your preferred editor
# git config --global color.ui true     # Enable colored output in Git

echo "Git configuration set for user $username with email $email."
