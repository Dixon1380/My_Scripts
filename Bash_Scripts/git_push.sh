#!/bin/bash

# Check if there are any uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "There are uncommitted changes. Please commit or stash them first."
    exit 1
fi

# Get the current branch name
branch=$(git rev-parse --abbrev-ref HEAD)

# Push changes to GitHub
echo "Pushing changes to GitHub..."
git push origin $branch

echo "Push successful!"
