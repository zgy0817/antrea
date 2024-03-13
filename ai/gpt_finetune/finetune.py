from openai import OpenAI
from pathlib import Path
import argparse
from utils import parse_cfg_file

'''
This script will first process the arguments and configurations, then choose the right form of the command that submitting fine-tuning job.
The job-submitting takes 2 steps: upload the formatted training data file, then create the fine-tuning job.
The fine-tuning job id will be shown in stdout.
'''

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