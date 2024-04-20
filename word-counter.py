import os
from collections import Counter
from tqdm import tqdm

def count_words(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        word_count = Counter(file.read().split())
    return sum(word_count.values())

def main(directory):
    count = 0
    total = 0
    for filename in tqdm(os.listdir(directory)):
        total += 1
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            words = count_words(filepath)
            if words < 300:
                print(filename)
                break
    print("Total files: " + str(total))
    print("More than 400 words: " + str(count))
# Replace 'directory_path' with the path to your directory
directory_path = '../raw-digest'
main(directory_path)
