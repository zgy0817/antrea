import argparse
import json
from utils import dicts_to_jsonl, parse_cfg_file

'''
The input data json file should match the data format in the "../vicuna/dataset/example.json".
It will first convert the input json into data_list, which is formatted, then dump it into the jsonl file.
'''

DEFAULT_SYS_PROMPT = "You are the assistant that helps classifying issues in Antrea, a software providing networking and security services for a Kubernetes cluster. Please only output the classification results as some words, which are closed by apostrophes and connected by comma."
DEFAULT_TASK_TYPE = "answering"

parser = argparse.ArgumentParser(description='This script will process the json data to the right jsonl format.')
parser.add_argument('-i', '--input', type=str, help='Input json file path')
parser.add_argument('-o', '--output', type=str, help='Output jsonl file path')
parser.add_argument('-c', '--config', type=str, help='Data processing configuration')
args = parser.parse_args()

input_file = args.input
output_file = args.output

if args.config:
    cfg_dict = parse_cfg_file(args.config)
    if 'sys_prompt' in cfg_dict:
        sys_prompt = cfg_dict['sys_prompt']
    else:
        sys_prompt = DEFAULT_SYS_PROMPT
    if 'task_type' in cfg_dict:
        task_type = cfg_dict['task_type']
    else:
        task_type = DEFAULT_TASK_TYPE
else:
    sys_prompt = DEFAULT_SYS_PROMPT
    task_type = DEFAULT_TASK_TYPE
 
f = open(input_file, 'r')
raw_data = json.load(f)
f.close()

data_list = []
for elem in raw_data:
    new_elem = {}
    messages = []
    reply_label = elem['conversations'][1]['value']
    if task_type == "classification":
        reply_label = reply_label.lstrip('[').rstrip(']').replace(' ', '')
    messages.append({"role": "system", "content": sys_prompt})
    messages.append({"role": "user", "content": elem['conversations'][0]['value']})
    messages.append({"role": "assistant", "content": reply_label})
    new_elem.update({"messages":messages})
    data_list.append(new_elem)

dicts_to_jsonl(data_list, output_file)
