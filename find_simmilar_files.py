#!/usr/bin/python3
import os
import difflib
import sys
import time
from threading import Thread

def format_time(seconds):
    intervals = (
        ('years', 31536000),
        ('months', 2592000),
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1)
    )
    
    result = []
    for name, count in intervals:
        value = int(seconds // count)
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append(f'{value} {name}')
    return ', '.join(result)

def possible_pairs(n):
    pairs = (n * (n-1)) // 2
    return pairs

def find_similar_files(folder_path):
    files = os.listdir(folder_path)
    similar_files = []
    total = possible_pairs(len(files))
    checked = 0
    start_time = time.time()
    for i in range(len(files)):
        for j in range(i+1, len(files)):
            checked = checked + 1
            percent = (checked / total) * 100
            elapsed_time = time.time() - start_time
            if percent > 0:
                eta = format_time((elapsed_time * (100 - percent)) / percent)
            else:
                eta = 0
            sys.stdout.write(f'\rComparing file {i+1} of {len(files)} ({percent:.2f}%), ETA: {eta}')
            sys.stdout.flush()
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
