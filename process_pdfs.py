import subprocess
import yaml
import os
import shutil

def exec_latex(latex_code, output_file):
    with open("temp.tex", "w") as f:
        f.write(latex_code)
    subprocess.run(["pdflatex", "temp.tex"], check=True)
    shutil.move("temp.pdf", output_file)
    os.remove("temp.tex")
    os.remove("temp.log")
    os.remove("temp.aux")

# Function to create a title page with large text
def create_title_page(title, output_file):
    title_latex = f"""
    \\documentclass{{article}}
    \\usepackage[utf8]{{inputenc}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1in}}
    \\begin{{document}}
    \\thispagestyle{{empty}}
    \\centering
    \\vspace*{{\\fill}}
    \\Huge
    {title}
    \\vspace*{{\\fill}}
    \\newpage
    \\end{{document}}
    """
    exec_latex(title_latex, output_file)

# Function to generate LaTeX code for the ToC
def generate_latex_toc(entries, output_file):
    toc_entries_latex = ""
    for entry in entries:
        title = entry["title"]
        page_number = entry["current_page"]
        toc_entries_latex += f"\\item {title} \\dotfill {page_number}\n"
    
    latex_code = f"""
    \\documentclass{{article}}
    \\usepackage[utf8]{{inputenc}}
    \\usepackage{{geometry}}
    \\geometry{{left=1in, right=1in, top=1in, bottom=1in}}

    \\begin{{document}}

    \\title{{Table of Contents}}
    \\maketitle

    \\begin{{enumerate}}
    {toc_entries_latex}
    \\end{{enumerate}}

    \\end{{document}}
    """
    exec_latex(latex_code, output_file)

# Function to run pdfjam with given options
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

def get_page_count(pdf_file):
    # Check if file exists
    if not os.path.isfile(pdf_file):
        print(f"File '{pdf_file}' not found!")
        return

    # Get the number of pages in the PDF
    result = subprocess.run(['pdfinfo', pdf_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout
    for line in output.splitlines():
        if "Pages:" in line:
            page_count = int(line.split(":")[1].strip())
            return page_count
    else:
        print("Could not determine the number of pages in the PDF.")
        raise Exception("Could not determine the number of pages in the PDF.")

def ensure_odd_pages(pdf_file, invert=False):
    page_count = get_page_count(pdf_file)

    if (page_count % 2 == 0) != invert:
        subprocess.run(['convert', 'xc:none', '-page', 'A4', 'blank.pdf'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        temp_pdf_path = f"{os.path.splitext(pdf_file)[0]}_temp.pdf"
        subprocess.run(['pdfunite', pdf_file, "blank.pdf", temp_pdf_path])

        os.replace(temp_pdf_path, pdf_file)

        print(f"A blank page has been added. The file '{pdf_file}' has been updated.")

        os.remove("blank.pdf")
    else:
        print("The page count is odd. No changes made.")

def add_page_numbers(output_file, tmp_output_file):
    latex_command = f"""
    \\documentclass[twoside]{{article}}
    \\usepackage[a4paper, margin=1in]{{geometry}} % Adjust the bottom margin
    \\usepackage{{fancyhdr}}
    \\usepackage{{pdfpages}}

    \\fancyhf{{}} % Clear all header and footer fields
    \\renewcommand{{\\headrulewidth}}{{0pt}} % Remove the header line

    % Define the page numbers' positions
    \\fancyfoot[LE]{{\\thepage}} % Left on Even pages
    \\fancyfoot[RO]{{\\thepage}} % Right on Odd pages

    \\begin{{document}}

    \\includepdf[pages=1-,pagecommand={{\\thispagestyle{{fancy}}}}]{{{tmp_output_file}}}

    \\end{{document}}
    """
    exec_latex(latex_command, output_file)

# Function to process the YAML configuration and run pdfjam
def process_pdf_files(config_file, output_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    toc_entries = []
    current_page = 3
    intermediate_files = []

    # Process each file defined in the YAML config
    for i, entry in enumerate(config['files']):
        title = entry['title']
        input_file = os.path.join('input', entry['file'])
        nup_format = entry['format']
        slides = entry['slides']
        
        # Create title page
        title_page_file = f'title_{i}.pdf'
        create_title_page(title, title_page_file)
        intermediate_files.append(title_page_file)
        
        # Ensure title page is on an odd page
        toc_entries.append({"title": title, "current_page": current_page})
        current_page += 1  # Title page counts as one page
        
        # Generate content file with pdfjam
        content_file = f'content_{i}.pdf'
        run_pdfjam(input_file, content_file, nup_format, slides)
        intermediate_files.append(content_file)
        
        # Ensure content ends on an odd page
        ensure_odd_pages(content_file)

        # Calculate number of pages in the content file
        page_count = get_page_count(content_file)
        current_page += page_count

    # Create a table of contents page
    toc_file = 'toc.pdf'
    generate_latex_toc(toc_entries, toc_file)
    ensure_odd_pages(toc_file, invert=True)
    intermediate_files.insert(0, toc_file)

    tmp_output_file = "output_tmp.pdf"

    # Combine all intermediate files into the final output file
    combine_command = ['pdfjam', '--outfile', tmp_output_file] + intermediate_files
    subprocess.run(combine_command, check=True)

    # Add page numbers to the output file
    add_page_numbers(output_file, tmp_output_file)
    intermediate_files.append(tmp_output_file)
    
    # Clean up intermediate files
    for file in intermediate_files:
        os.remove(file)

# Example usage
config_file = 'config.yaml'  # Replace with your actual config file path
output_file = 'output/output.pdf'  # Desired output file name
process_pdf_files(config_file, output_file)
