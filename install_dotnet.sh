#!bin/bash

#download script 

wget https://dot.net/v1/dotnet-install.sh -O dotnet-install.sh

sudo chmod +x ./dotnet-install.sh

./dotnet-install.sh --version latest

./dotnet-install.sh --version latest --runtime aspnetcore

./dotnet-install.sh --channel 7.0 


echo ".NET is installed"
