import Levenshtein
import json
import re
import os

def filter_by_levenshtein_ratio(strings, input_string, threshold=0.85):
    result = []
    for s in strings:
        score = Levenshtein.ratio(s, input_string)
        if score > threshold:
            result.append((s, score))
    return result


def match_item(input_string) -> None | tuple:
    if 'pro ks' in input_string:
        output_string = re.sub(r'\bpro\b', 'professional', input_string)
        output_string = re.sub(r'\bks\b', 'killstreak', output_string)
    elif 'spec ks' in input_string:
        output_string = re.sub(r'\bspec\b', 'specialized', input_string)
        output_string = re.sub(r'\bks\b', 'killstreak', output_string)
    elif 'ks' in input_string.split():
        output_string = re.sub(r'\bks\b', 'killstreak', input_string)
    else:
        output_string = input_string
    
    current_directory = os.path.dirname(__file__)
    extras_dir = os.path.join(current_directory, 'extras')
    if os.path.isdir(extras_dir):
        json_file_path = os.path.join(extras_dir, 'item_list.json')

    with open(json_file_path, 'r') as file:
        item_list = json.load(file)

    filtered_strings = filter_by_levenshtein_ratio(item_list, output_string)

    # Filter out to get one item with the highest score
    highest_score = -1
    highest_tuple = None

    for item in filtered_strings:
        string, score = item
        if score > highest_score:
            highest_score = score
            highest_tuple = item

    return(highest_tuple)

if __name__ == '__main__':
    result = match_item('strange rocket launcher')
    print(result[0])