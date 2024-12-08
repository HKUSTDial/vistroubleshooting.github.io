import json
from collections import Counter
import pandas as pd
import math
import os
import numpy as np
from pathlib import Path

def get_all_keys(json_data):
    keys = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            keys.append(key)
            keys.extend(get_all_keys(value))
    elif isinstance(json_data, list):
        for item in json_data:
            keys.extend(get_all_keys(item))
    return keys

def filter_json(json_data, keys_to_filter):
    if isinstance(json_data, dict):
        filtered_data = {
            key: filter_json(value, keys_to_filter) if key in keys_to_filter else ""
            for key, value in json_data.items()
        }
        return filtered_data
    if isinstance(json_data, list):
        return [filter_json(item, keys_to_filter) for item in json_data]
    return json_data

def process_single_file(json_data):

    KEYfilter = pd.read_csv(r"keys.csv")#calculate the keys from Vegalite schema
    key_list = KEYfilter['key'].tolist()

    filter_tmp = [x for x in key_list if x not in ["datasets", "values"]]
    filtered_data = filter_json(json_data, filter_tmp)
        
    all_keys = get_all_keys(filtered_data)

    filtered_keys = []
    for x in all_keys:
        if x in key_list:  
            filtered_keys.append(x)

    num_keys = len(filtered_keys)

    if num_keys <= 16:
        keys_type = "Simple"
    elif num_keys <= 24:
        keys_type = "Medium"
    elif num_keys <= 41:
        keys_type = "Complex"
    else:
        keys_type = "Extra Complex"
        
    return {
            'keys_type': keys_type,
            'keys_number': num_keys
        }
    

def main():
    df = pd.read_excel(r"dataset/3_validCode_cases/288_Vega.xlsx", 
                      sheet_name="Sheet1")
    
    results = []
    
    for index, row in df.iterrows():
        question_id = row['Question ID']
        title = row['Title']
        
        result_row = {
            'Question ID': question_id,
            'Title': title,
            'Question Code Type': None,
            'Question Code Keys Number': None,
            'Answer Code Type': None,
            'Answer Code Keys Number': None
        }

        if isinstance(row['Question Code'], str):
            try:
                question_json = json.loads(row['Question Code'])
                question_result = process_single_file(question_json)
                if question_result:
                    result_row.update({
                        'Question Code Type': question_result['keys_type'],
                        'Question Code Keys Number': question_result['keys_number']
                    })
            except json.JSONDecodeError:
                result_row.update({
                    'Question Code Type': "null",
                    'Question Code Keys Number': "null"
                })
        
        if isinstance(row['Answer Code'], str):
            try:
                answer_json = json.loads(row['Answer Code'])
                answer_result = process_single_file(answer_json)
                if answer_result:
                    result_row.update({
                        'Answer Code Type': answer_result['keys_type'],
                        'Answer Code Keys Number': answer_result['keys_number']
                    })
            except json.JSONDecodeError:
                result_row.update({
                    'Answer Code Type': "null",
                    'Answer Code Keys Number': "null"
                })
        
        results.append(result_row)

    with open(r'Q2/Code_complexity/Output/forum_key_results_1.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main() 