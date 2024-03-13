# Vicuna Model Deployment and Training Documentation

## Table of Contents
<!-- toc -->
- [Vicuna Model Deployment and Training Documentation](#vicuna-model-deployment-and-training-documentation)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Deployment](#deployment)
    - [1.Get the Vicuna model](#1get-the-vicuna-model)
    - [2.Build container with Vicuna](#2build-container-with-vicuna)
    - [3.Check if the model can repsonse](#3check-if-the-model-can-repsonse)
    - [4.Interactive with the model](#4interactive-with-the-model)
  - [Fine-tuning](#fine-tuning)
    - [1.Get the model and dataset](#1get-the-model-and-dataset)
    - [2.Build container for training](#2build-container-for-training)
      - [Full-parameter](#full-parameter)
      - [QLoRA](#qlora)
<!-- /toc -->

## Introduction

[Vicuna model](https://lmsys.org/blog/2023-03-30-vicuna/) is an open-source chatbot model trained by fine-tuning LLaMA on user-shared conversations collected from ShareGPT. It has superior performance compared to LLaMA and Alpaca, even approaching the performance of ChatGPT, evaluted by GPT-4 and with comparably low training costs. The code and model parameters [in open access with github](https://github.com/lm-sys/FastChat).

This document will focus on deploying and fine-tuning Vicuna model. We re-encapsulate the FastChat API for Vicuna in docker container, make it easier for personal use. Currently, it works well with the lastest version of vicuna-7b-v1.5-16k and FastChat(v0.2.33). Please check the [version compatibility between Vicuna and FastChat](https://github.com/lm-sys/FastChat/blob/main/docs/vicuna_weights_version.md) if there's any issues of version.

Before deployment, you should have **GPU** in your system, with **enough GPU memory** [**(14GB for Vicuna-7B and 28GB for Vicuna-13B)**](https://github.com/lm-sys/FastChat#single-gpu). Also, make sure that **docker, docker-compose, nvidia-docker, jq** are installed in your Linux system.

If you want to fine-tune the model with **full parameters**, you should have **4 * A100 GPU(80GB)** in your system, with the same software requirements as deployment. Fine-tuning in **QLoRA** is a more efficient way that only need **1 * A10 GPU(24GB)**.

## Deployment

### 1.Get the Vicuna model
Firstly, you should get the Vicuna model you want to deploy. For original Vicuna model, Please check the [model weights](https://github.com/lm-sys/FastChat#model-weights) and download the model you want to use. Make sure the model repository is set in folder "./antrea/ai/vicuna/model".

You can run the following command to download the model from the corresponding HuggingFace repository.
```plain
cd ./antrea/ai/vicuna/model
git lfs clone <huggingface_repo>
```
For example, for deployment of model "vicuna-7b-v1.5-16k", you should have "./antrea/ai/vicuna/model/vicuna-7b-v1.5-16k" repository in your antrea folder. After the model being set ready, you should change to the "./antrea/ai/vicuna/deploy" directory:
```plain
cd ../deploy
```
We use Dockerfile to build docker container, so you need to have root privilege to run docker commands.
### 2.Build container with Vicuna

The environment variables MODEL_PATH and MODEL_NAMES should be set for build Vicuna container, you can either set it manually or pass the arguments to "build.sh" when running the command. 
```plain
sudo sh build.sh -p <vicuna_model_path> -n <model_name>
```
Attention, the MODEL_PATH should be the path in docker container, which maps the "./antrea/ai/vicuna/model" into "/model". For example, "/model/vicuna-7b-v1.5-16k" for <vicuna_model_path>. The MODEL_NAMES can be randomly named by your preference.

Since the docker-compose command in "build.sh", "sudo" is needed. This Shell scripts will first set the environment variables and then run the docker-compose to build container according to "docker-compose.yml" file, it needs 1-2 minutes or so. After container created successfully, you can send request to the url: [http://0.0.0.0:8000/v1/chat/completions](http://0.0.0.0:8000/v1/chat/completions)
### 3.Check if the model can repsonse

```plain
sh call.sh
```
It will send POST request to call the model, and return the model reponses. If the responses are like this, the model has been deployed successfully. 
```plain
{"id":"chatcmpl-UFWP9BqDg3s7DDfc5eXLS3","object":"chat.completion","created":1701329914,"model":"vicuna","choices":[{"index":0,"message":{"role":"assistant","content":"Sure! Here are three numbers between 1 and 10:\n\n1. 5\n2. 8\n3. 9"},"finish_reason":"stop"}],"usage":{"prompt_tokens":51,"total_tokens":81,"completion_tokens":30}} 
```
If the container has not been built, it may return this message, and you should wait for a while. If it consistently returns this message, there might be an issue:
```plain
{"object":"error","message":"Only  allowed now, your model vicuna","code":40301} 
```
### 4.Interactive with the model

```plain
sh interactive.sh
```
You can chat with the deployed Vicuna model by running this Shell script. Feel free to ask any questions interactively to the model. To exit, simply press Ctrl+Z. Please note that the JSON processing tool **jq** is required for this operation.

## Fine-tuning

### 1.Get the model and dataset
For fine-tuning, you should set the Vicuna model and training dataset ready. Getting model shares the same steps as deployment, and training dataset should be collected in the form of json.
One sample of the json dataset file is like this:
```plain
    {
        "id": "1",
        "conversations": [
            {
                "from": "human",
                "value": "What is antctl and what are its different operating modes"
            },
            {
                "from": "gpt",
                "value": "Antctl is the command-line tool for Antrea, a significant component in the Kubernetes networking framework. It operates in three distinct modes: controller mode, agent mode, and standalone mode. In controller mode, it can connect to the Antrea Controller when run out-of-cluster or within the Controller Pod, enabling queries about network policies. In agent mode, when executed within an Antrea Agent Pod, it interacts with the local agent to provide information specific to that Agent, such as the set of computed Network Policies. The standalone mode is not explicitly described in the provided excerpt of the article."
            }
        ]
    },
```
An example is like "./antrea/ai/vicuna/dataset/example.json". After the model and dataset being set ready, you should change to the "./antrea/ai/vicuna/train_full" directory for full parameter fine-tuning, or "./antrea/ai/vicuna/train_qlora" for QLoRA fine-tuning.

### 2.Build container for training

Attention, all the path type environment variables like DATA_PATH, MODEL_PATH, MODEL_OUTPUT and so on are folders mapped to docker container, they should be set according to volume mapping in "docker-compose.yml". For example, set DATA_PATH into "/dataset/example.json" for host path "./antrea/ai/vicuna/dataset/example.json". We also mentioned this in deployment.

Some training parameters are not considered environment variables, such as "--save_steps", "--logging_steps", etc. You can change them in "docker-compose.yml" if you want.

#### Full-parameter
The environment variables NPROC_PER_NODE, PER_DEVICE_TRAIN_BATCH_SIZE, PER_DEVICE_EVAL_BATCH_SIZE,DATA_PATH, MODEL_PATH, MODEL_OUTPUT, NUM_TRAIN_EPOCHS, LEARNING_RATE, MODEL_MAX_LENGTH should be set for build Vicuna training container, you can either set it manually or in the ".env" file in the "train_full" folder. Default numerical values are already set.

Then, run the command below, to start the container and training.
```plain
docker-compose up
```

After traininig, your trained model will be saved in MODEL_OUTPUT folder(mapped back to host path), for further testing. 

#### QLoRA
The environment variables MODEL_PATH, DATA_PATH, MODEL_OUTPUT, GPU_NUM, NPROC_PER_NODE, NUM_TRAIN_EPOCHS, PER_DEVICE_TRAIN_BATCH_SIZE, PER_DEVICE_EVAL_BATCH_SIZE, LEARNING_RATE, MODEL_MAX_LENGTH, LORA_R should be set for build Vicuna QLoRA training container, you can either set it manually or in the ".env" file in the "train_qlora" folder. Default numerical values are already set.

Then, run the command below, to start the container and training.
```plain
docker-compose up
```

The QLoRA training uses deepspeed package, and the deepspeed configuration file in "./antrea/ai/vicuna/train_qlora/playground". You can change the configuration by creating new configuration files and sending it into the "--deepspeed" argument in "docker-compose.yml".

If you're suffering with out-of-memory error with your GPU, you may try setting your MODEL_MAX_LENGTH and LORA_R lower. If you want to fully utilize your GPU memory you can also increase them or increase the PER_DEVICE_TRAIN_BATCH_SIZE. You can also set some environment variables such as PYTORCH_CUDA_ALLOC_CONF by different sizes of "max_split_size_mb" for GPU memory management. For more information, please refer to [the official pytorch docs of cuda](https://pytorch.org/docs/stable/notes/cuda.html#environment-variables).

After traininig, your trained QLoRA adapter models will be saved in MODEL_OUTPUT folder(mapped back to host path), for further testing. For loading trained adapters with the model, please refer to [Huggingface PeftModel.from_pretrained()](https://huggingface.co/docs/peft/en/package_reference/peft_model#peft.PeftModel).

