import fitz_old as fitz
import re
import requests
from tqdm import tqdm
import os

directory = "input"
if not os.path.exists(directory):
    os.makedirs(directory)

# Define the keywords
keywords = ["VISTO:", "CONSIDERANDO:"]
last_key = ["R E S U E L V E :", "D I S P O N E :", "RESUELVE:", "DISPONE:"]

def remove_exp_fragment(text):
    # Define the regular expression pattern to match the fragment
    pattern = r'EXP-LUJ:\s*\d+/\d+'

    # Replace the matched fragment with an empty string
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text.strip()


def extract_sections(text) -> list[str]:
    # Split the text using regular expressions
    for key in last_key:
        if key in text:
            last = key
            break
    all_keywords = keywords + [last]

    sections = re.split("|".join(map(re.escape, all_keywords)), text)

    # Remove empty sections
    return [section.strip() for section in sections if section.strip()][-3:]


def parse_pdf_content(pdf_content, file_name):
    file_name = re.sub(r'/', '_', file_name)
    # Use fitz to open the PDF from binary content
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    text = ""
    for page in doc:  # iterate the document pages
        text += page.get_text()
        text = remove_exp_fragment(text)
        sections = extract_sections(text)
        # Write the main text to a file
        with open(os.path.join(directory, f"{file_name}.txt"), "w", encoding="utf-8") as file:
            file.write(text)

        # Create a text file for each section
        for i, section in enumerate(sections, start=1):
            section_filename = os.path.join(directory, f"{file_name}_section_{i}.txt")
            with open(section_filename, "w", encoding="utf-8") as section_file:
                section_file.write(section)


def process_pdf_from_url(pdf_url, index):
    # Make an HTTP GET request to download the PDF file
    response = requests.get(pdf_url, stream=True)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        try:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1]
        except:
            file_name = f"doc-{index}"

        with open('downloads-meta.txt', 'a', encoding="utf-8") as file:
            file.write(f"{file_name},{pdf_url}\n")
        # Pass the content of the response to the PDF parser
        parse_pdf_content(response.content, file_name)
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")


def download_documents(id_from: int, id_to: int):
    for i in tqdm(range(id_from, id_to + 1)):
        try:
            process_pdf_from_url(f"https://resoluciones.unlu.edu.ar/documento.view.php?cod={i}", i)
        except:
            continue
    return id_to + 1


with open('downloads-progress.txt', 'r') as file:
    # Read the single value from the file
    value = file.readline().strip()


for i in range(int(value), 135):
    print(f"\nProcessing batch num {i}")
    min = i * 1000
    max = min + 1000
    download_documents(min, max)

    with open('downloads-progress.txt', 'w', encoding="utf-8") as file:
        file.write(str(i + 1))
