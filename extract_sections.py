import re
import os

from tqdm import tqdm

# Define the k
keywords = ["VISTO:", "CONSIDERANDO:"]
last_key = ["R E S U E L V E", "D I S P O N E", "RESUELVE", "DISPONE"]

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

try:
    with open("extract-progress.txt") as progress:
        last_processed_file = int(progress.readline())
except:
    last_processed_file = 0
    print("No progress, using 0 as default")

try:
    for file in tqdm(os.listdir("../raw-digest")):
        last_processed_file += 1
        with open("../raw-digest/" + file) as f:
            text = f.read()
            sections = extract_sections(text, file)
            if len(sections) > 0:
                for idx, section in enumerate(sections):
                    with open(f"../digest-sections/{file}-section-{idx}.txt", "w") as output:
                        output.write(section)
except:
    print("Failure extracting sections from files")
    with open("extract-progress.txt", "w") as progress:
        progress.write(str(last_processed_file))
