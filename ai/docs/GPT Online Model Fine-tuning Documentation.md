# GPT Online Model Fine-tuning Documentation
## Introduction
GPT is a large-language-model that can give response to your questions in natural language, by calculating the representation of your questions with its model parameters. However, for customized scenarios, the original models OpenAI releases may not work very well. If you come across this problem, model fine-tuning may be a good solution. The working principle of fine-tuning is using your data which you want the model to learn, and adjusting the model parameters by back propagation algorithm with your data. It makes AI model following instructions better, as well as formatting output responses.

We have re-encapsulated the OpenAI model fine-tuning interface. This document describes how to use your own data to finetune an OpenAI GPT online model, just by following 3 steps: data preparing, fine-tuning job creating, and fine-tuned model calling. 

Before the fine-tuning process, you should have **Python3 Environment**, and **pip3** installed, and the **openai, pathlib** Python package installed. Up to now, it can run with the latest version of Python3 and the packages, and you could try other versions. For users already have Python3 and pip, you can use the following command to install packages in requirements.txt (same folder with the scripts).
```plain
pip3 install -r requirements.txt
```
Also, you should have an **OpenAI api-key** to run the fine-tuning jobs.

All the python scripts' usage can be shown with the command:
```plain
python3 <python_script> -h
```
For OpenAI official tutorial, please [refer to this](https://openai.com/blog/gpt-3-5-turbo-fine-tuning-and-api-updates), or [more specific one](https://platform.openai.com/docs/guides/fine-tuning).
<br></br>
## Steps
### 1. Prepare formatted data
First of all, you need to change to the working directory of gpt_finetune in antrea after cloning the repository:
```plain
cd ./antrea/ai/gpt_finetune
```
The data are prepared to **jsonl** format, where each line is an effective json object, representing a training sample. An example of official formatted training sample for gpt-3.5-turbo fine-tuning is like this.

```plain
{
  "messages": [
    { "role": "system", "content": "You are an assistant that occasionally misspells words" },
    { "role": "user", "content": "Tell me a story." },
    { "role": "assistant", "content": "One day a student went to schoool." }
  ]
}
```
The "content" of the "system" is the systematic prompt describes what general task you want the model to do, or which format you want the model to output. The "content" of the "user" is the specific task you want the model to do. The "content" of the "assistant" is the expected model outputs. 
You need to adjust your data format into the official one. Suppose you have a raw data format like this, named "input.json":

```plain
 {
  "id": "identity_1",
  "conversations": [
   {
    "from": "human",
    "value": "title: Egress should not be applied to traffic destined for ServiceCIDRs. body: **Describe the bug**\r\n\r\nThe issue was reported by @sroot1986, @claknee, @robbo10:\r\n\r\nWhen AntreaProxy is asked to skip some Services by configuring `skipServices` or is not running at all, the traffic destined for Service ClusterIP is supposed to reach host network and be proxied by kube-proxy, or be processed by the host directly (e.g. [NodeLocal DNSCache](https://kubernetes.io/docs/tasks/administer-cluster/nodelocaldns/)). However, if Egress is applied to the Pod, the traffic would be forwarded to Egress Node and would be proxied remotely, as opposed to locally, which could incur  performance issue and unexpected behaviors.\r\n\r\n\r\n**To Reproduce**\r\n\r\n\r\n1. Install [NodeLocal DNSCache](https://kubernetes.io/docs/tasks/administer-cluster/nodelocaldns/)\r\n2. Configure AntreaProxy to skip DNS service, following [the doc](https://github.com/antrea-io/antrea/blob/main/docs/antrea-proxy.md#when-you-are-using-nodelocal-dnscache)\r\n3. Apply Egress to a Pod, which is scheduled to a Node different from the Egress Node.\r\n4. Trigger DNS query from the Pod, the Node local DNS server won't receive the request and the resolution may fail\r\n\r\n**Expected**\r\n\r\n\r\nPod-to-Service ClusterIP should not be forwarded to Egress Node and should be handled locally regardless of how AntreaProxy is configured.\r\n\r\n**Versions:**\r\n\r\n - Antrea version (Docker image tag). v1.11.3, v1.12.2, v1.13.1\r\n\r\n"
   },
   {
    "from": "gpt",
    "value": "['transit']"
   }
  ]
 },
```
You can run the python script named "data_process.py" to convert it into the right form named "output.jsonl".
```plain
python3 data_process.py --input input.json --output output.jsonl --config data_process.cfg
```
Or:
```plain
python3 data_process.py -i input.json -o output.jsonl -c data_process.cfg
```
The "data_process.cfg" file is to set the system prompt for the data. And also the task type, which is either "answering" or "classification", related to label processing. A sample is like this in below. Please pay attention to the names of configurations, which should be matched precisely.
```plain
sys_prompt = You are a helpful assistant.
task_type = classification
```
This script will first convert the raw json file formatted above, into a Python data_list,  then dump it into the jsonl file. If your raw data show a different format, you can write your own script to process it into the right jsonl form.

### 2. Create a fine-tuning job

Once the formatted data finished, a fine-tuning job can be created by three ways. We only en-capsulate the Python way, which is recommended to use.

As for Python, you can run the script named "finetune.py" to submit the fine-tuning job, and the job id will be returned after created. Remember to replace <your_api_key> by your own OpenAI api key.

```plain
python3 finetune.py -k <openai_api_key> -d output.jsonl
```
Or:
```plain
python3 finetune.py --key <openai_api_key> --data output.jsonl
```
This is default training setting-up. For setting hyper-parameters (batch_size, learning_rate_multiplier, n_epochs) and validation file, please write the configuration file like this in "train.cfg". Please pay attention to the names of configurations, which should be matched precisely.
```plain
openai_api_key = <openai_api_key>
training_file = <training_file>
model = gpt-3.5-turbo
n_epochs = 3
batch_size = 1
learning_rate_multiplier = 2
validation_file = <validation_file>
```
Then run the command:
```plain
python3 finetune.py --config train.cfg
```
Or:
```plain
python3 finetune.py -c train.cfg
```
Once your fine-tuning job created, you can get the training status [on the website](https://platform.openai.com/finetune). For the original python API, please refer to [OpenAI API](https://platform.openai.com/docs/api-reference/fine-tuning/create).

As for Linux Shell (with curl installed), you can run the 'curl' command to upload your file with environment variables set up. As for the simplest UI way, you can go [official website UI](https://platform.openai.com/finetune) to submit fine-tuning jobs, by clicking "Create new". Please refer to official website if you want to create fine-tuning jobs in these ways.

### 3. Use a fine-tuned model
To use a fine-tuned model, you can run the command below, and the model's answer will be returned in stdout. The fine-tuned model name can be acquired on [your OpenAI account](https://platform.openai.com/finetune/).

```plain
python3 infer.py --key <openai_api_key> --model <model_name> -q <your_question>
```
The model name can also be acquired using the fine-tuning job id, which will be outputed right after fine-tuning job created. So you could just input the fine-tuning job id to call the model.
```plain
 python3 infer.py --key <openai_api_key> --job <ft_job_id> -q <your_question>
```
To customize the prompt, you can write a configuration file for testing. Please pay attention to the names of configurations, which should be matched precisely. An example is like this in "infer.cfg":
```plain
openai_api_key = <openai_api_key>
ft_job_id = <job_id>
model = <model_name>
max_tokens = <max_tokens>
temperature = 0
sys_prompt = <your_prompt>
user_input = <your_question>
```
Then run the command below. The model's response will be returned.
```plain
python3 infer.py --config infer.cfg
```

## Code Explanation
As for the "data_process.py" in Step 1, it matches the data format in the "Supposed" paragraph. It will first convert the input json into data_list, which is formatted, then dump it into the jsonl file. The dicts_to_jsonl function is implemented in "utils.py" within the same folder.

```plain
import argparse
import json
from utils import dicts_to_jsonl, parse_cfg_file

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
    label = elem['conversations'][1]['value']
    if task_type == "classification":
        label = label.lstrip('[').rstrip(']').replace(' ', '')
    messages.append({"role": "system", "content": sys_prompt})
    messages.append({"role": "user", "content": elem['conversations'][0]['value']})
    messages.append({"role": "assistant", "content": label})
    new_elem.update({"messages":messages})
    data_list.append(new_elem)

dicts_to_jsonl(data_list, output_file)
```

As for the "finetune.py" in Step 2, the script will first process the arguments and configurations, then choose the right form of the command that submitting fine-tuning job. The job-submitting takes 2 steps: upload the formatted training data file, then create the fine-tuning job. The fine-tuning job id will be shown in stdout.

```plain
from openai import OpenAI
from pathlib import Path
import argparse
from utils import parse_cfg_file

parser = argparse.ArgumentParser(description='This script will upload your formatted training file and create the fine-tuning job.')
parser.add_argument('-k', '--key', type=str, help='OpenAI API key')
parser.add_argument('-d', '--data', type=str, help='Training data in jsonl')
parser.add_argument('-c', '--config', type=str, help='Training configuration')
args = parser.parse_args()

if args.config:
    cfg_dict = parse_cfg_file(args.config)
    if 'n_epochs' in cfg_dict:
        cfg_dict['n_epochs'] = int(cfg_dict['n_epochs'])
    else:
        cfg_dict['n_epochs'] = 3
    if 'batch_size' in cfg_dict:
        cfg_dict['batch_size'] = int(cfg_dict['batch_size'])
    else:
        cfg_dict['batch_size'] = 1
    if 'learning_rate_multiplier' in cfg_dict:
        cfg_dict['learning_rate_multiplier'] = float(cfg_dict['learning_rate_multiplier'])
    else:
        cfg_dict['learning_rate_multiplier'] = 2

    parser.set_defaults(**cfg_dict)
    args = parser.parse_args() # Overwrite arguments

    train_data = args.training_file
    client = OpenAI(api_key=args.openai_api_key)

    train_file_object = client.files.create(
        file=Path(train_data),
        purpose="fine-tune",
    )

    if hasattr(args, "validation_file"):
        valid_file_object = client.files.create(
            file=Path(args.validation_file),
            purpose="fine-tune",
        )

        ft_job = client.fine_tuning.jobs.create(
            training_file=train_file_object.id,
            validation_file=valid_file_object.id,
            model=args.model, 
            hyperparameters={
                "n_epochs":args.n_epochs,
                "learning_rate_multiplier":args.learning_rate_multiplier,
                "batch_size":args.batch_size
            }
        )
    else:
        ft_job = client.fine_tuning.jobs.create(
            training_file=train_file_object.id,
            model=args.model, 
            hyperparameters={
                "n_epochs":args.n_epochs,
                "learning_rate_multiplier":args.learning_rate_multiplier,
                "batch_size":args.batch_size
            }
        )

else:
    train_data = args.data
    client = OpenAI(api_key=args.key)

    train_file_object = client.files.create(
        file=Path(train_data),
        purpose="fine-tune",
    )

    ft_job = client.fine_tuning.jobs.create(
        training_file=train_file_object.id,
        model="gpt-3.5-turbo"
    )

print(ft_job.id)
```

The "infer.py" in Step 3 is in the same structure as "finetune.py", it will first process the arguments and configurations, then call the corresponding API for chat completions. If the model name isn't set, the fine-tuning job id will be used to get the model name.

```plain
from openai import OpenAI
import argparse
from utils import parse_cfg_file

parser = argparse.ArgumentParser(description='This script will call your fine-tuned model to answer your question.')
parser.add_argument('-k', '--key', type=str, help='OpenAI API key')
parser.add_argument('-j', '--job', type=str, help='Fine-tuning job-id')
parser.add_argument('-m', '--model', type=str, help='Fine-tuned model name')
parser.add_argument('-q', '--question', type=str, help='Your question')
parser.add_argument('-c', '--config', type=str, help='Inferring configuration')
args = parser.parse_args()

if args.config:
    cfg_dict = parse_cfg_file(args.config)
    if 'max_tokens' in cfg_dict:
        cfg_dict['max_tokens'] = int(cfg_dict['max_tokens'])
    else:
        cfg_dict['max_tokens'] = 2048
    if 'temperature' in cfg_dict:
        cfg_dict['temperature'] = float(cfg_dict['temperature'])
    else:
        cfg_dict['temperature'] = 1

    parser.set_defaults(**cfg_dict)
    args = parser.parse_args() # Overwrite arguments

    client = OpenAI(api_key=args.openai_api_key)
    if args.model:
        ft_model_name = args.model
    else:
        ft_job_id = args.ft_job_id
        ft_model_name = client.fine_tuning.jobs.retrieve(ft_job_id).fine_tuned_model
        assert(ft_model_name is not None), "The fine-tune job {} may be failed or unfinished!".format(ft_job_id)

    if hasattr(args, "max_tokens") or hasattr(args, "temperature"):
        response = client.chat.completions.create(
            model=ft_model_name,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            messages=[
                {"role": "system", "content": args.sys_prompt},
                {"role": "user", "content": args.user_input}
            ]
        )
    else:
        response = client.chat.completions.create(
            model=ft_model_name,
            messages=[
                {"role": "system", "content": args.sys_prompt},
                {"role": "user", "content": args.user_input}
            ]
        )
else:
    client = OpenAI(api_key=args.key)
    if args.model:
        ft_model_name = args.model
    else:
        ft_job_id = args.job
        ft_model_name = client.fine_tuning.jobs.retrieve(ft_job_id).fine_tuned_model
        assert(ft_model_name is not None), "The fine-tune job {} may be failed or unfinished!".format(ft_job_id)

    response = client.chat.completions.create(
        model=ft_model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": args.question}
        ]
    )

print(response.choices[0].message.content)
```

## FAQ

