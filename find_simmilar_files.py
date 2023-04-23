#!/usr/bin/python3
import os
import Levenshtein
import sys
import time
from multiprocessing import Process, Queue

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

def compare_pairs(folder_path, pairs, result_queue):
    for pair in pairs:
        i, j = pair
        file1 = files[i]
        file2 = files[j]
        file1_name, _ = os.path.splitext(file1)
        file2_name, _ = os.path.splitext(file2)
        ratio = Levenshtein.ratio(file1_name, file2_name)
        if ratio > 0.8:
            result_queue.put((file1, file2))

def find_similar_files(folder_path):
    global files
    files = os.listdir(folder_path)
    similar_files = []
    pairs = []
    total = possible_pairs(len(files))
    sys.stdout.write(f'pairs to check {total}\n')
    sys.stdout.flush()
    checked = 0
    start_time = time.time()
    for i in range(len(files)):
        for j in range(i+1, len(files)):
            pairs.append((i, j))
            checked = checked + 1
            percent = (checked / total) * 100
            elapsed_time = time.time() - start_time
            if percent > 0:
                eta = format_time((elapsed_time * (100 - percent)) / percent)
            else:
                eta = 0
            sys.stdout.write(f'\rComparing file {i+1} of {len(files)} ({percent:.2f}%), ETA: {eta}')
            sys.stdout.flush()
    print()
    result_queue = Queue()
    chunk_size = 100000
    chunks = [pairs[i:i + chunk_size] for i in range(0, len(pairs), chunk_size)]
    processes = []
    for chunk in chunks:
        process = Process(target=compare_pairs, args=(folder_path, chunk, result_queue))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    while not result_queue.empty():
        similar_files.append(result_queue.get())
    return similar_files

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
folder_path = os.path.join(script_dir, 'icons')

similar_files = find_similar_files(folder_path)
for file1, file2 in similar_files:
    print(f'{file1}\t{file2}')
