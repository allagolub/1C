#!/usr/bin/env python3

from os import path, access, walk
from os.path import getsize
from os import R_OK

from math import ceil, floor


def read_input():
    first_directory = input("Enter the path of the first directory: ")
    second_directory = input("Enter the path of the second directory: ")
    similarity_threshold = int(input("Enter the similarity threshold: "))
    return first_directory, second_directory, similarity_threshold


def check_access(directory):
    if path.exists(directory) and path.isdir(directory) and access(directory, R_OK):
        return True
    raise FileNotFoundError("Directory does not exist or is not readable")


def get_accessable_files(directory):
    has_access = []
    for root, _, files in walk(directory):
        for file in files:
            path_to_file = path.join(root, file)
            if access(path_to_file, R_OK):
                has_access.append(path_to_file)
    return has_access


def get_size_to_files_map(files):
    size_to_files = {}
    max_size = 0
    for file in files:
        size = getsize(file)
        max_size = max(max_size, size)
        size_to_files[size] = size_to_files.get(size, []) + [file]
    return size_to_files, max_size


def get_files_similarity(first_file, second_file):
    file1 = open(first_file, 'rb')
    file2 = open(second_file, 'rb')

    file1_symbol_map = {}
    file2_symbol_map = {}

    are_fully_identical = True

    lines1 = file1.readlines()
    lines2 = file2.readlines()

    if len(lines1) != len(lines2):
        are_fully_identical = False

    till = min(len(lines1), len(lines2))

    for i in range(till):
        line1 = lines1[i].rstrip().decode('utf-8', 'ignore')
        line2 = lines2[i].rstrip().decode('utf-8', 'ignore')

        if len(line1) != len(line2):
            are_fully_identical = False
            
        line_till = min(len(line1), len(line2))
        for j in range(line_till):
            if line1[j] != line2[j]:
                are_fully_identical = False

            file1_symbol_map[line1[j]] = file1_symbol_map.get(line1[j], 0) + 1
            file2_symbol_map[line2[j]] = file2_symbol_map.get(line2[j], 0) + 1

        for j in range(line_till, len(line1)):
            are_fully_identical = False
            file1_symbol_map[line1[j]] = file1_symbol_map.get(line1[j], 0) + 1

        for j in range(line_till, len(line2)):
            are_fully_identical = False
            file2_symbol_map[line2[j]] = file2_symbol_map.get(line2[j], 0) + 1

    for i in range(till, len(lines1)):
        are_fully_identical = False
        line1 = lines1[i].rstrip().decode('utf-8', 'ignore')
        for j in range(len(line1)):
            file1_symbol_map[line1[j]] = file1_symbol_map.get(line1[j], 0) + 1

    for i in range(till, len(lines2)):
        are_fully_identical = False
        line2 = lines2[i].rstrip().decode('utf-8', 'ignore')
        for j in range(len(line2)):
            file2_symbol_map[line2[j]] = file2_symbol_map.get(line2[j], 0) + 1

    file1.close()
    file2.close()

    similar_symbols = 0
    file1_symbol_count = 0
    file2_symbol_count = 0
    all_symbols = set(file1_symbol_map.keys()) | set(file2_symbol_map.keys())
    for symbol in all_symbols:
        count1 = file1_symbol_map.get(symbol, 0)
        file1_symbol_count += count1
        count2 = file2_symbol_map.get(symbol, 0)
        file2_symbol_count += count2
        similar_symbols += min(count1, count2)

    if max(file1_symbol_count, file2_symbol_count) == 0:
        return 100, True

    similarity_percentage = similar_symbols / max(file1_symbol_count, file2_symbol_count) * 100      
    return similarity_percentage, are_fully_identical


def find_similar_files(first_directory, second_directory, similarity_threshold):
    first_files = get_accessable_files(first_directory)
    second_files = get_accessable_files(second_directory)

    first_size_to_files, _ = get_size_to_files_map(first_files)
    second_size_to_files, second_max_size = get_size_to_files_map(second_files)

    identical_files = []
    similar_files = []

    first_has_identical_in_second = set()
    second_has_identical_in_first = set()

    from_size = 0
    to_size = second_max_size

    for first_size, first_size_files in first_size_to_files.items():
        if similarity_threshold != 0 and first_size != 0:
            from_size = ceil(first_size * similarity_threshold / 100)
            to_size = floor(first_size / (first_size * similarity_threshold / 100))

        for second_size in range(from_size, to_size + 1):
            second_size_files = second_size_to_files.get(second_size, [])
            for first_file in first_size_files:
                for second_file in second_size_files:
                    similarity_percentage, are_fully_identical = get_files_similarity(first_file, second_file)
                    if are_fully_identical:
                        identical_files.append((first_file, second_file))
                        first_has_identical_in_second.add(first_file)
                        second_has_identical_in_first.add(second_file)
                    if similarity_percentage >= similarity_threshold:
                        similar_files.append((first_file, second_file, similarity_percentage))

    return identical_files, similar_files, set(first_files) - first_has_identical_in_second, set(second_files) - second_has_identical_in_first


def main():
    first_directory, second_directory, similarity_threshold = read_input()
    check_access(first_directory)
    check_access(second_directory)
    id_files, sim_files, in_first, in_second = find_similar_files(first_directory, second_directory, similarity_threshold)
    for file1, file2 in id_files:
        print(f"{file1} - {file2}")
    for file1, file2, similarity in sim_files:
        print(f"{file1} - {file2} - {similarity}%")
    for file in in_first:
        print(f"{file}")
    for file in in_second:
        print(f"{file}")


if __name__ == '__main__':
    main()