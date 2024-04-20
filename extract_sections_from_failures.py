import re
import os

from tqdm import tqdm

# Define the k
keywords = ["VISTO:", "CONSIDERANDO:"]
last_key = ["ARTÍCULO  1°", "ARTICULO  1º"]

file = open('new-failures.txt', 'w')
file.close()
def extract_sections(text, file_name) -> list[str]:
    # Split the text using regular expressions
    last = None

    for key in last_key:
        if key in text:
            last = key
            break

    if last is None:
        print(f"Error in extracting sections from file: {file_name}")
        with open('new-failures.txt', 'a') as file:
            file.write(file_name)
        return []

    all_keywords = keywords + [last]
    text = re.sub(r'\s+', ' ', text)

    sections = re.split("|".join(map(re.escape, all_keywords)), text)

    # Remove empty sections
    return [section.strip() for section in sections if section.strip()][-3:]

try:
    with open("failures.txt") as failures:
        for failed_file_name in failures:
            with open("../raw-digest/" + failed_file_name.strip()) as failed_file:
                text = failed_file.read()
                if len(text) > 0:
                    sections = extract_sections(text, failed_file_name)
                    if len(sections) > 0:
                        for idx, section in enumerate(sections):
                            with open(f"../digest-sections/{failed_file_name}-section-{idx}.txt", "w") as output:
                                output.write(section)
                else:
                    print("Empty file " + failed_file.name)
except Exception as e:
    print("Something went wrong: " + str(e))

