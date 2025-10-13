import os
import re
import json
import pandas as pd
from tqdm import tqdm
import numpy as np
from sklearn.model_selection import train_test_split


data_dir = "xxxxxxxxxx"

json_input_path = "xxxxxxxxxxxxxxxxx"

output_json_path = os.path.join(data_dir, "xxxxxxxxxxxxxxx")



with open(json_input_path , 'r', encoding='utf-8') as json_file:
    fine_data = json.load(json_file)


for key, item in fine_data.items():
    reason_generate = item["reason_generate"]
    item["sys"] = reason_generate


with open(output_json_path, "w", encoding="utf-8") as f_out:
    json.dump(fine_data, f_out, ensure_ascii=False, indent=4)

print(f"finished：{output_json_path}")



with open(json_interprtation_path, "r", encoding="utf-8") as f:
    interpretion_data = json.load(f)

interpretation_map = {}
for item in interpretion_data:
    dialogue_id = item["dialogue_id"]
    dialogue = item["dialogue"]
    interpretations = [turn.get("interpretation") for turn in dialogue]
    interpretation_map[dialogue_id] = interpretations


merged_data = []


for item in fine_data:
    dialogue_id = item["dialogue_id"]
    dialogue = item["dialogue"]

    interpretations = interpretation_map.get(dialogue_id, [])

    new_dialogue = []
    for idx, turn in enumerate(dialogue):
        interpretation = interpretations[idx] if idx < len(interpretations) else None

        new_turn = turn.copy()
        if interpretation:
            new_turn["interpretation"] = interpretation

        new_dialogue.append(new_turn)

    merged_data.append({
        "dialogue_id": dialogue_id,
        "dialogue": new_dialogue
    })


with open(output_json_path, "w", encoding="utf-8") as f_out:
    json.dump(merged_data, f_out, ensure_ascii=False, indent=4)

print(f"finished:{output_json_path}")



