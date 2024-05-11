import re
import os

from tqdm import tqdm

DISPONE_BASE_DIR = "collection/completa/dispone/"
RESUELVE_BASE_DIR = "collection/completa/resuelve/"

BASE_OUTPUT_DIR = "collection"

VISTO_DIR = f"{BASE_OUTPUT_DIR}/visto"
CONSIDERANDO_DIR = f"{BASE_OUTPUT_DIR}/considerando"
RESUELVE_DIR = f"{BASE_OUTPUT_DIR}/resuelve"
DISPONE_DIR = f"{BASE_OUTPUT_DIR}/dispone"

# Define the k
keywords = ["VISTO:", "CONSIDERANDO:"]
last_key = ["R E S U E L V E", "D I S P O N E", "RESUELVE", "DISPONE"]

def create_directories():
    if not os.path.exists(VISTO_DIR):
        os.mkdir(VISTO_DIR)

    if not os.path.exists(CONSIDERANDO_DIR):
        os.mkdir(CONSIDERANDO_DIR)

    if not os.path.exists(RESUELVE_DIR):
        os.mkdir(RESUELVE_DIR)

    if not os.path.exists(DISPONE_DIR):
        os.mkdir(DISPONE_DIR)

def extract_sections(text, file_name) -> list[str]:
    # Split the text using regular expressions
    last = None

    for key in last_key:
        if key in text:
            last = key
            break

    if last is None:
        print(f"Error in extracting sections from file: {file_name}")
        with open('failures.txt', 'a') as file:
            file.write(file_name + '\n')
        return []

    all_keywords = keywords + [last]
    text = re.sub(r'\s+', ' ', text)

    sections = re.split("|".join(map(re.escape, all_keywords)), text)

    # Remove empty sections
    return [section.strip() for section in sections if section.strip()][-3:]


def extract_sections_and_write_to_file(base_dir, last_section_dir):
    failures = []
    for file in tqdm(os.listdir(base_dir)):
        if file.endswith(".txt"):
            with open(base_dir + "/" + file) as f:
                text = f.read()
                sections = extract_sections(text, file)
                if len(sections) == 3:
                    with open(f"{VISTO_DIR}/{file}", "w") as output:
                        output.write(sections[0])
                    with open(f"{CONSIDERANDO_DIR}/{file}", "w") as output:
                        output.write(sections[1])
                    with open(f"{BASE_OUTPUT_DIR}/{last_section_dir}/{file}", "w") as output:
                        output.write(sections[2])
                else:
                    failures.append(file)

create_directories()
failures_resuelve = extract_sections_and_write_to_file(RESUELVE_BASE_DIR, "resuelve")
failures_dispone = extract_sections_and_write_to_file(DISPONE_BASE_DIR, "dispone")

if failures_dispone is not None and failures_resuelve is not None:
    with open('preprocessors/sections_splitter/failures.txt', 'w') as file:
        file.writelines(str(failures_resuelve))
        file.writelines(str(failures_dispone))