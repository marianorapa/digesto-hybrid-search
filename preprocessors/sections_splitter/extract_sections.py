import re
import os
import logging
#from tqdm import tqdm
from utils.file_eraser import erase_file_from_everywhere

BASE_OUTPUT_DIR = "./collection"

DISPONE_BASE_DIR = f"{BASE_OUTPUT_DIR}/completa/dispone/"
RESUELVE_BASE_DIR = f"{BASE_OUTPUT_DIR}/completa/resuelve/"

VISTO_DIR = f"{BASE_OUTPUT_DIR}/visto/documents"
CONSIDERANDO_DIR = f"{BASE_OUTPUT_DIR}/considerando/documents"
RESUELVE_DIR = f"{BASE_OUTPUT_DIR}/resuelve/documents"
DISPONE_DIR = f"{BASE_OUTPUT_DIR}/dispone/documents"

BASE_DIR = "./preprocessors/sections_splitter"

# Define the k
keywords = ["VISTO:", "CONSIDERANDO:"]
last_key = ["R E S U E L V E", "D I S P O N E", "RESUELVE", "DISPONE"]

def create_directories():
    if not os.path.exists(VISTO_DIR):
        os.makedirs(VISTO_DIR)

    if not os.path.exists(CONSIDERANDO_DIR):
        os.makedirs(CONSIDERANDO_DIR)

    if not os.path.exists(RESUELVE_DIR):
        os.makedirs(RESUELVE_DIR)

    if not os.path.exists(DISPONE_DIR):
        os.makedirs(DISPONE_DIR)

def extract_sections_from_text_and_save_to_file(text, file_name) -> list[str]:
    # Split the text using regular expressions
    last = None

    for key in last_key:
        if key in text:
            last = key
            break

    if last is None:
        logging.error(f"Error in extracting sections from file: {file_name}")
        with open(f'{BASE_DIR}/failures.txt', 'a') as file:
            file.write(file_name + '\n')
        erase_file_from_everywhere(file_name, "MISSING_LAST_SECTION")
        return []

    all_keywords = keywords + [last]
    text = re.sub(r'\s+', ' ', text)

    sections = re.split("|".join(map(re.escape, all_keywords)), text)

    # Remove empty sections
    return [section.strip() for section in sections if section.strip()][-3:]


def extract_sections_and_write_to_file(base_dir, last_section_dir):
    failures = []
    for file in os.listdir(base_dir):
        if file.endswith(".txt"):
            with open(base_dir + "/" + file) as f:
                text = f.read()
                sections = extract_sections_from_text_and_save_to_file(text, file)
                if len(sections) == 3:
                    with open(f"{VISTO_DIR}/{file}", "w") as output:
                        output.write(sections[0])
                    with open(f"{CONSIDERANDO_DIR}/{file}", "w") as output:
                        output.write(sections[1])
                    with open(f"{BASE_OUTPUT_DIR}/{last_section_dir}/{file}", "w") as output:
                        output.write(sections[2])
                else:
                    failures.append(file)

def extract_sections():
    logging.info("Sections Splitter Started")

    create_directories()
    failures_resuelve = extract_sections_and_write_to_file(RESUELVE_BASE_DIR, "resuelve")
    failures_dispone = extract_sections_and_write_to_file(DISPONE_BASE_DIR, "dispone")

    if failures_dispone is not None and failures_resuelve is not None:
        with open('preprocessors/sections_splitter/failures.txt', 'w') as file:
            file.writelines(str(failures_resuelve))
            file.writelines(str(failures_dispone))