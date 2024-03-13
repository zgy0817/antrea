from openai import OpenAI
import argparse
from utils import parse_cfg_file

'''
This script will first process the arguments and configurations, then call the corresponding API for chat completions.
If the model name isn't set, the fine-tuning job id will be used to get the model name.
'''

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