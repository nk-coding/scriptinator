#!/bin/bash

if [ -d "input" ]; then
  echo "Input directory found"
else
  echo "Error: Directory 'input' does not exist."
  exit 1
fi

# Check if the file exists
if [ -f "config.yaml" ]; then
  echo "Config file found"
else
  echo "Error: File 'config.yaml' does not exist."
  exit 1
fi

# Build the Docker image
docker build -t pdf_processor .

mkdir -p output

# Run the Docker container
docker run --rm \
    -v "$(pwd)/input:/workspace/input" \
    -v "$(pwd)/output:/workspace/output" \
    -v "$(pwd)/config.yaml:/workspace/config.yaml" \
    pdf_processor

# The output file will be saved in the output directory
echo "PDF processing complete. Check the 'output' directory for the results."
