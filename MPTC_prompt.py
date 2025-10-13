import os
from openai import OpenAI
from difflib import SequenceMatcher
# import backoff
import re
import json
from tqdm import tqdm

client = OpenAI(
    api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)


def ask_gpt(chat_history, situation, persona, character, therapist):

    user_prompt = "User Input: {}".format(chat_history)

    sys_prompt = f"""
    You are a professional therapist responsible for providing efficient emotional support and helping users alleviate their distress. Your task is to carefully analyze each user's personality type and characterisc, then tailor your communication style to best alleviate their distress. Please follow these steps:
1. Analyze the User's Personality:
The speaker's personality type is {persona}, his specific traits are: {traits}. Please assess their preferred communication style based on these characteristics.

2. Explain the Psychological Rationale:
The therapist’s “Golden Response” is: {therapist}. This response is guided by the strategy: {strategy}, which is tailored to the user's personality type. Explain the rationale behind the therapist’s response in the context of the user’s personality traits, and describe how these traits shape the user’s emotional needs and communication preferences.

3. Generate a Tailored Response
Based on the user's personality type {persona}, choose a therapist strategy from the following list and then generate a concise, empathetic, and solution‑focused reply that directly addresses the user’s expressed concerns. Align your tone and language with the user’s preferred communication style to maximize comfort and clarity.
    - Open Questions  
    - Approval  
    - Self-Disclosure  
    - Restatement  
    - Interpretation  
    - Advisement  
    - Communication Skills  
    - Structuring the Therapy  
    - Guiding the Pace and Depth of the Conversation  
    - Others
**Note that you just choose one strategy from the list.**

### Example
- **User Input:**  
“I don’t know if I’m able to talk today, Paul. I shouldn’t have come. I should have just… called it off. I’m sorry.”  
- **Personality Type:** Te  
- **Personality Traits:** Emphasizes logic and objective facts; prefers rules, structure, and actionable solutions.  
- **Interpretation:** This individual values efficiency, clear reasoning, and concrete steps. Their communication style is direct, data‑driven, and focused on practical outcomes.   
- **Therapist Response:**   “Are you all right?”

# Note that the Therapist Response should be concise.

    """
    messages = [
        {
            "role": "system", 
            "content": sys_prompt
        },
        {
            "role": "user", 
            "content": user_prompt
        }
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        temperature= 0.3,
        max_tokens= 2000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    answer = chat_completion.choices[0].message.content



    return answer

    
# process_ort_file("data", "data_process")
def numerical_sort_key(filename):
    match = re.search(r'(\d+)(?=\.\w+$)', filename)
    if match:
        return int(match.group(1))
    return float('inf')

qa_store = []

def parse_response(text):
    """Extracts information from the given response text."""
    # Define patterns to extract each piece of information
    strategy_pattern = re.search(r'\*\*(.*?):\*\*\s*(.*?)(?:\.|$)', text, re.DOTALL)
    response_pattern = re.search(r'\*\*.*?:\*\*\s*(.*)', text, re.DOTALL)
    extracted_data = {}
    if strategy_pattern:
        extracted_data['Strategy'] = strategy_pattern.group(1).strip()
    else:
        extracted_data['Strategy'] = "check: No valid strategy format found"
    if response_pattern:
        extracted_data['Response'] = response_pattern.group(1).strip()
    else:
        extracted_data['Response'] = text.strip()
    

    return extracted_data

def parse_response4(input_string):
    # Splitting the input string by '<' and '>'
    # This will help in isolating each segment like user, strategy, system, and response
    parts = input_string.split('<')
    data = {}
    
    # Loop through each part and extract the necessary information
    for part in parts:
        if 'user>' in part:
            data['user_emotion'] = part.split('>')[1].strip()
        elif 'strategy>' in part:
            data['strategy'] = part.split('>')[1].strip()
        elif 'system>' in part:
            data['system_emotion'] = part.split('>')[1].strip()
        elif 'cls>' in part:
            data['response'] = part.split('>')[1].strip()
    
    return data

def parse_response4o(input_string):
    data = {}

    # Using regular expressions to match the pattern for 'Strategy' and 'Response'
    # strategy_pattern = r"(?:\*\*Communication Strategy:\*\*|\- \*\*Chosen Communication Strategy:\*\*)\s*(.*?)\s*\n" **Chosen Strategy:** - **Chosen Strategy:**  **Determine the Communication Strategy:**
    strategy_pattern = r"(?:- )?\*\*(?:Communication Strategy|Chosen Communication Strategy|Determine the Communication Strategy):\*\*\s*(.*?)\s*\n"
    # response_pattern = r"(?:\*\*Response:\*\*|\*\*Tailored Response:\*\*)\s*([\s\S]+)"
    response_pattern =r"(?:- )?\*\*(?:Therapist Response|Tailored Response|Output):\*\*\s*([\s\S]+)"
    #- **Preferred Communication Style:**  - **Influence on Emotional Needs:**  ### Explain the Psychological Rationale  ### Interpretation:
    # response_pattern = r"(?:- )?\*\*(?:Response|Tailored Response|Output):\*\*\s*([\s\S]+)"

    # Extracting Communication Strategy
    strategy_match = re.search(strategy_pattern, input_string,re.IGNORECASE)
    communication_strategy = strategy_match.group(1).strip() if strategy_match else "Not Found"
    # communication_strategy = strategy_match.group(2).strip() if strategy_match else "Not Found"
    # Extracting Communication Strategy

    # Interpretation = Interpretation_match.group(2).strip() if Interpretation_match else "Not Found"


    # Extracting Tailored Response
    response_match = re.search(response_pattern, input_string, re.DOTALL | re.IGNORECASE)
    if response_match:
        tailored_response = response_match.group(1).strip()
    else:
        tailored_response = "Not Found: " + input_string.strip()  # Store the whole input if response is not found

    # Store extracted values in the dictionary
    data["strategy"] = communication_strategy
    data["response"] = tailored_response

    return data



qa_store=[]
def generate_QA(input_QA_dir):
    filenames = os.listdir(input_QA_dir)
    sorted_filenames = sorted(filenames, key=numerical_sort_key)
    for fname in sorted_filenames:
        fpath = os.path.join(input_QA_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            for chat_line in f:
                chat_line = chat_line.strip()
                answer = ask_gpt(chat_line)
                print("========== chat {} ==========".format(fpath))
                print("answer is:", answer)
                parsed_data = parse_response4o(answer)
                qa_store.append({'Question': chat_line, 'Answer': parsed_data})
                print(qa_store)

    with open('qa_store4o.json', 'w', encoding='utf-8') as json_file:
        json.dump(qa_store, json_file, ensure_ascii=False, indent=4)
        
def generate_ESC(input_QA_dir):
    fname = "gpt_test.json"
    output_dir = "gpt_test_response"
    fpath = os.path.join(input_QA_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f) 
        for item in tqdm(data, desc="Processing", unit="item"):

            file_id =  item["file_id"]
            speaker = item["speaker"]
            chat_line = item["text"]
            persona = item["persona"]
            Characteristics = item["Characteristics"]
            chat_line = chat_line.strip()
            persona_l = [persona]
            characteristics = Characteristics.split(", ")
            file_name = file_id[-1]

            result_fpath = os.path.join(output_dir, file_name)
            # print(chat_line)
            # asdfsdfsdsdsd,
            answer = ask_gpt(chat_line,persona_l, characteristics)
            print("========== chat {} ==========".format(file_id))
            print("answer is:", answer)
            parsed_data = parse_response4o(answer)
            # qa_store.append({
            #     'file_id':file_id,
            #     'text': chat_line, 
            #     'persona':persona, 
            #     'Characteristics':Characteristics,
            #     'Response': parsed_data
            # })

            gpt_data= {
                'file_id':file_id,
                'speaker':speaker,
                'persona':persona, 
                'Characteristics':Characteristics,
                'text': chat_line, 
                'gpt4o': parsed_data
            }
            # print(qa_store)


            with open(result_fpath, 'w', encoding='utf-8') as json_file:
                json.dump(gpt_data, json_file, ensure_ascii=False, indent=4)
    

def generate_Intreatment(input_QA_dir):
    fname = "gpt_test.json"
    output_dir = "gpt_test_response"
    fpath = os.path.join(input_QA_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f) 
        for item in tqdm(data, desc="Processing", unit="item"):
            dialogue_id =  item["dialogue_id"]
            situation = item["situation"]
            persona = item["Personality"]
            persona_l = [persona]
            characteristics = item["Characteristics"]
            # characteristics = Characteristics.split(", ")
            dialog=item["dialog"]
            file_id = "dialogue_{}".format(dialogue_id)
            result_fpath = os.path.join(output_dir, file_id)
            # if os.path.exists(result_fpath):
            #     print(f" Skip '{file_id}' (already exists).")
            #     continue

            dialogue_data = {
            "dialogue_id": dialogue_id,
            "situation": situation,
            "persona": persona,
            "characteristics": characteristics,
            "dialogue": [] 
            }

            for item in dialog:
                user_input = item["user"]
                sys_gold = item["sys"]
                strat = item["strat"]
                raw_session = item["raw_session"]
                chat_line = user_input.strip()
                # print(chat_line)
                # asdfsdfsdsdsd,chat_history, situation, persona, character, therapist
                answer = ask_gpt(chat_line,situation, persona_l, characteristics,sys_gold )
                print("========== chat {} ==========".format(file_id))
                print("answer is:", answer)
                parsed_data = parse_response4o(answer)
            # qa_store.append({
            #     'file_id':file_id,
            #     'text': chat_line, 
            #     'persona':persona, 
            #     'Characteristics':Characteristics,
            #     'Response': parsed_data
            # })

                gpt_data= {
                    'user_input':user_input,
                    'sys':sys_gold,
                    'persona':persona, 
                    'Characteristics':characteristics,
                    'gpt4o': parsed_data,
                    # 'raw_session':raw_session
                }

                dialogue_data["dialogue"].append(gpt_data)


            with open(result_fpath, 'w', encoding='utf-8') as json_file:
                json.dump(dialogue_data, json_file, ensure_ascii=False, indent=4)


            

raw_data = "data"
process_data="data_process"
segment_data = "data_split"

generate_Intreatment("data_persona")



print("finished the generating!")


        


