import subprocess
import yaml
import os

# Function to run the pdfjam command with given options
def run_pdfjam(input_file, output_file, nup_format, slides):
    slides_str = ','.join(map(str, slides))
    command = [
        'pdfjam',
        '--outfile', output_file,
        '--nup', nup_format,
        '--a4paper',
        '--', input_file,
        slides_str
    ]
    subprocess.run(command, check=True)

# Function to process the YAML configuration and run pdfjam
def process_pdf_files(config_file, output_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    intermediate_files = []
    for i, entry in enumerate(config['files']):
        input_file = os.path.join('input', entry['name'])
        nup_format = entry['format']
        slides = entry['slides']
        
        # Generate intermediate file names
        intermediate_file = f'intermediate_{i}.pdf'
        intermediate_files.append(intermediate_file)
        
        # Run pdfjam for each entry
        run_pdfjam(input_file, intermediate_file, nup_format, slides)
    
    # Combine all intermediate files into the final output file
    combine_command = ['pdfjam', '--outfile', output_file] + intermediate_files
    subprocess.run(combine_command, check=True)
    
    # Clean up intermediate files
    for file in intermediate_files:
        os.remove(file)

# Example usage
config_file = 'config.yaml'  # Replace with your actual config file path
output_file = 'output/output.pdf'   # Desired output file name
process_pdf_files(config_file, output_file)
