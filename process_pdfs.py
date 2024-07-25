import subprocess
import yaml
import os

# Function to create a title page with large text
def create_title_page(title, output_file):
    title_latex = f"""
    \\documentclass{{article}}
    \\usepackage[utf8]{{inputenc}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1in}}
    \\begin{{document}}
    \\centering
    \\vspace*{{\\fill}}
    \\Huge
    {title}
    \\vspace*{{\\fill}}
    \\newpage
    \\end{{document}}
    """
    with open("title.tex", "w") as f:
        f.write(title_latex)
    subprocess.run(["pdflatex", "title.tex"], check=True)
    os.rename("title.pdf", output_file)
    os.remove("title.tex")
    os.remove("title.log")
    os.remove("title.aux")

# Function to run pdfjam with given options
def run_pdfjam(input_file, output_file, nup_format, slides):
    slides_str = ','.join(map(str, slides))
    command = [
        'pdfjam',
        '--outfile', output_file,
        '--nup', nup_format,
        '--a4paper',
        '--pagenumber',
        '--', input_file,
        slides_str
    ]
    subprocess.run(command, check=True)

# Function to add an empty page if necessary to maintain odd page number
def ensure_odd_pages(pdf_file):
    output_file = pdf_file.replace('.pdf', '_odd.pdf')
    command = [
        'pdfjam', pdf_file,
        '--outfile', output_file,
    #    '--suffix', '',
        '--evenpages', 'no',
        '--lastpage', '{empty}'
    ]
    subprocess.run(command, check=True)
    os.remove(pdf_file)
    os.rename(output_file, pdf_file)

# Function to process the YAML configuration and run pdfjam
def process_pdf_files(config_file, output_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    toc_entries = []
    current_page = 1
    intermediate_files = []

    # Process each file defined in the YAML config
    for i, entry in enumerate(config['files']):
        title = entry['title']
        input_file = os.path.join('input', entry['name'])
        nup_format = entry['format']
        slides = entry['slides']
        
        # Create title page
        title_page_file = f'title_{i}.pdf'
        create_title_page(title, title_page_file)
        intermediate_files.append(title_page_file)
        
        # Ensure title page is on an odd page
        ensure_odd_pages(title_page_file)
        toc_entries.append(f"{title}: {current_page}")
        current_page += 1  # Title page counts as one page
        
        # Generate content file with pdfjam
        content_file = f'content_{i}.pdf'
        run_pdfjam(input_file, content_file, nup_format, slides)
        intermediate_files.append(content_file)
        
        # Calculate number of pages in the content file
        page_count = int(subprocess.check_output(['pdfinfo', content_file]).decode().split('Pages:')[1].strip())
        current_page += page_count
        
        # Ensure content ends on an odd page
        ensure_odd_pages(content_file)

    # Create a table of contents page
    toc_file = 'toc.pdf'
    create_title_page("Table of Contents\n\n" + "\n".join(toc_entries), toc_file)
    intermediate_files.insert(0, toc_file)

    # Combine all intermediate files into the final output file
    combine_command = ['pdfjam', '--outfile', output_file] + intermediate_files
    subprocess.run(combine_command, check=True)
    
    # Clean up intermediate files
    for file in intermediate_files:
        os.remove(file)

# Example usage
config_file = 'config.yaml'  # Replace with your actual config file path
output_file = 'output/output.pdf'  # Desired output file name
process_pdf_files(config_file, output_file)
