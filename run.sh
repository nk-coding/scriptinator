#!/bin/bash

# Build the Docker image
docker build -t pdf_processor .

# Run the Docker container
docker run --rm \
    -v "$(pwd)/input:/workspace/input" \
    -v "$(pwd)/output:/workspace/output" \
    -v "$(pwd)/config.yaml:/workspace/config.yaml" \
    pdf_processor

# The output file will be saved in the output directory
echo "PDF processing complete. Check the 'output' directory for the results."
