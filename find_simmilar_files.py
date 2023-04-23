#!/usr/bin/python3
import os
import difflib
import sys

def find_similar_files(folder_path):
    files = os.listdir(folder_path)
    similar_files = []
    for i in range(len(files)):
        sys.stdout.write(f'\rComparing file {i+1} of {len(files)}')
        sys.stdout.flush()
        for j in range(i+1, len(files)):
            file1_name, _ = os.path.splitext(files[i])
            file2_name, _ = os.path.splitext(files[j])
            ratio = difflib.SequenceMatcher(None, file1_name, file2_name).ratio()
            if ratio > 0.8:
                similar_files.append((files[i], files[j]))
    print()
    return similar_files

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
folder_path = os.path.join(script_dir, 'icons')

similar_files = find_similar_files(folder_path)
for file1, file2 in similar_files:
    print(f'{file1}\t{file2}')
