# Vicuna Model Deployment and Training Documentation
## Introduction

[Vicuna model](https://lmsys.org/blog/2023-03-30-vicuna/) is an open-source chatbot model trained by fine-tuning LLaMA on user-shared conversations collected from ShareGPT. It has superior performance compared to LLaMA and Alpaca, even approaching the performance of ChatGPT, evaluted by GPT-4 and with comparably low training costs. The code and model parameters [in open access with github](https://github.com/lm-sys/FastChat).

This document will focus on deploying and fine-tuning Vicuna model. We re-encapsulate the FastChat API for Vicuna, make it easier for personal use. Currently, it works well with the lastest version of vicuna-7b-v1.5-16k and FastChat(v0.2.33). Please check the [version compatibility between Vicuna and FastChat](https://github.com/lm-sys/FastChat/blob/main/docs/vicuna_weights_version.md) if there's any issues of version.

Before use, you should have **GPU** in your system, with **enough GPU memory** [**(14GB for Vicuna-7B and 28GB for Vicuna-13B)**](https://github.com/lm-sys/FastChat#single-gpu). Also, make sure that **docker, docker-compose, nvidia-docker, jq** are installed in your Linux system.

## Deployment

### 1.Get the Vicuna model
Firstly, you should get the Vicuna model you want to deploy. For original Vicuna model, Please check the [model weights](https://github.com/lm-sys/FastChat#model-weights) and download the model you want to use. Make sure the model repository is set in folder "./antrea/ai/vicuna/model".

You can run the following command to download the model from the corresponding HuggingFace repository.
```plain
cd ./antrea/ai/vicuna/model
git lfs clone <huggingface_repo>
```
For example, for deployment of model "vicuna-7b-v1.5-16k", you should have "./antrea/ai/vicuna/model/vicuna-7b-v1.5-16k" repository in your antrea folder. After the model being set ready, you should change to the "./antrea/ai/vicuna/deploy* directory:
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

TODO

