import json

# REF: https://ml-gis-service.com/index.php/2022/04/27/toolbox-python-list-of-dicts-to-jsonl-json-lines/
def dicts_to_jsonl(data_list: list, filename: str) -> None:
    sjsonl = '.jsonl'
    # Check filename
    if not filename.endswith(sjsonl):
        filename = filename + sjsonl
    # Save data
    with open(filename, 'w') as out:
        for ddict in data_list:
            jout = json.dumps(ddict) + '\n'
            out.write(jout)

def parse_cfg_file(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("user_input") or line.startswith("sys_prompt"):
                key, value = handle_user_input(line)
                config[key] = value
                continue
            line = line.strip()
            if '#' in line:
                cmt_index = line.index('#')
                line = line[:cmt_index]
            if line:
                try:
                    key, value = line.split('=')
                except:
                    continue
                key = key.strip()
                value = value.strip()
                config[key] = value
    return config

def handle_user_input(line):
    line = line.strip()
    index1 = line.find('=')
    if index1 < 0:
        ValueError("Invalid input line: {}".format(line))
    key = line[0:index1].strip()
    value = line[index1+1:].strip()
    return key, value
