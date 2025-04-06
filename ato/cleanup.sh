#!/bin/bash

# Script to clean up project files

echo "Cleaning up project files..."

# Create backup directory if it does not exist
if [ ! -d "./backup" ]; then
  mkdir -p ./backup
  echo "Created backup directory"
fi

# Backup important configuration files
echo "Backing up important configuration files..."
cp -f .env ./backup/ 2>/dev/null || echo "No .env to backup"
cp -f theme.json ./backup/ || echo "No theme.json to backup"
cp -f package.json ./backup/ || echo "No package.json to backup"
cp -f tsconfig.json ./backup/ || echo "No tsconfig.json to backup"
cp -f drizzle.config.ts ./backup/ || echo "No drizzle.config.ts to backup"

# Remove duplicate project folder
if [ -d "./vovi" ]; then
  echo "Removing duplicate vovi directory..."
  rm -rf ./vovi
fi

# Remove log files except for the most recent one
echo "Cleaning log files..."
find ./logs -type f -name "*.log" | sort | head -n -1 | xargs rm -f 2>/dev/null
rm -f ./sample.log

# Remove temp files and attached_assets directory
echo "Removing temporary files and assets..."
rm -rf ./temp
rm -rf ./attached_assets

echo "Cleanup finished!"
