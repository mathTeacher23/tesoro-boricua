import os
import json
import re

# Path to the folder containing your JSON files
FOLDER_PATH = 'data/raw/raw_tesoro'  # <-- change this to your actual folder path
DESTINATION_PATH = 'data/preprocessed/preprocessed_tesoro'

# Regular expression to extract the letter from filenames like 'tesoro_letter_a.json'
filename_pattern = re.compile(r'tesoro_letter_([a-zñ])\.json', re.IGNORECASE)

for filename in os.listdir(FOLDER_PATH):
    match = filename_pattern.match(filename)
    if not match:
        continue  # Skip files that don't match the pattern

    letter = match.group(1).upper()  # Extract letter and capitalize it
    filepath = os.path.join(FOLDER_PATH, filename)

    # Load the original JSON data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Transform the dictionary to a list of entries
    transformed = []
    for term, es_definitions in data.items():
        entry = {
            "letter": letter,
            "term": term,
            "es_definitions": es_definitions,
            "en_definitions": [],  # Placeholder for English definitions
            "source": "https://tesoro.pr"
        }
        transformed.append(entry)

    # Save transformed data back to a new file or overwrite the original
    output_path = os.path.join(DESTINATION_PATH, f'transformed_{filename}')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(transformed, f, ensure_ascii=False, indent=2)

    print(f"Transformed {filename} -> {output_path}")