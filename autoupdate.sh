#!/bin/bash

echo "Checking for updates...."

sudo apt update && sudo apt upgrade -y

# Check if reboot is needed
if [ -f /var/run/reboot-required ]; then
  echo "System updates have been applied that require a reboot."
  
  # Prompt the user
  read -p "Do you want to reboot now? (y/n): " answer

  # Check the user's answer
  case $answer in
    [Yy]* ) 
      echo "Rebooting now..."
      sudo reboot
      ;;
    [Nn]* ) 
      echo "Reboot canceled. Please remember to reboot later."
      ;;
    * ) 
      echo "Invalid response. Reboot will not be performed."
      ;;
  esac
else
  echo "System is up-to-date. No restart is needed at this time."
fi




