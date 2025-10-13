import os
import re
import json
import pandas as pd
from tqdm import tqdm
import numpy as np
from collections import defaultdict

data_dir = "xxxxxxxxxxxxxxx"

def numerical_sort_key(filename):
    # match = re.search(r'(\d+)(?=\.\w+$)', filename)
    match = re.search(r'(?:utt_|frame_)(\d+)', filename)  
    if match:
        return int(match.group(1))
    return float('inf')

filenames = os.listdir(data_dir)
conv_len = len(filenames)
print(conv_len)
sorted_filenames = sorted(filenames, key=numerical_sort_key)

# dialogues =  defaultdict(lambda: {"dialogue_id": None, "dialog": []})
dialogues =  []

for fname in sorted_filenames:
    data_path = os.path.join(data_dir, fname)
    with open(data_path, 'r',encoding='utf-8') as file:
        json_data = json.load(file)
        file_id = json_data["file_id"]
        # speaker = json_data["speaker"]
        persona = json_data["persona"]
        characteristics = json_data["Characteristics"]
        text = json_data["text"]
        response = json_data["answer_mbti"]

        
        if response.endswith('.'):
            response = response[:-1]
        # # pseu_strategy = json_data["gpt4o"].get("strategy")
        # interpretation = json_data["gpt4o"].get("interpretation")
        # reason_generate =  json_data["gpt4o"].get("response")

        # if speaker =="Client":
        #     MBTI_predict = "Si"
        # else:
        #     MBTI_predict = "nondetection"
            
        # dialog_item = {
        #     "speaker": speaker,
        #     "emotion": json_data["emotion"],
        #     "strategy": json_data["strategy"],
        #     "text": json_data["text"],
        #     # "cognitive": json_data["answer_detection"],
        #     "MBTI_predict": json_data["answer_detection"]
        # }
        # item = {
        #     "file_id": file_id,
        #     "speaker": speaker,
        #     "persona": persona,
        #     "characteristics": characteristics,
        #     "text": text,
        #     # "pseu_strategy": pseu_strategy,
        #     "interpretation":interpretation,
        #     "reason_generate": reason_generate
        #     # "cognitive": json_data["answer_detection"],
        #     # "MBTI_predict": json_data["answer_detection"]
        # }

        item = {
            "file_id": file_id,
            # "speaker": speaker,
            "persona": persona,
            "characteristics": characteristics,
            "text": text,
            "response": response
        }


        # dialogues[dialogue_id]["dialogue_id"] = dialogue_id
        # dialogues[dialogue_id]["dialog"].append(dialog_item)
        dialogues.append(item)

# sorted_dialogues = sorted(dialogues.values(), key=lambda x: x["dialogue_id"])

output_dir = "xxxxxxxxxxxxxxxx"
output_path = os.path.join(output_dir, 'xxxxxxxxxxxxxxxxxxx')
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(dialogues, file, ensure_ascii=False, indent=4)
    
print("finished")
