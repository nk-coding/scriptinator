# Use the latest texlive image
FROM texlive/texlive:latest

# Update package lists and install necessary packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip

RUN apt-get install -y poppler-utils

# Install Python packages
RUN pip3 install pyyaml --break-system-packages

# Set the working directory
WORKDIR /workspace

# Copy the Python script and YAML config
COPY process_pdfs.py ./

# Create input and output directories
RUN mkdir -p input output

# Entry point for the container
CMD ["python3", "process_pdfs.py"]
