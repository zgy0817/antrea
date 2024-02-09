FROM nvidia/cuda:12.2.0-devel-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=CST-8
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:64

RUN apt-get update -y && apt-get install -y python3.9 python3.9-distutils curl \
  && apt-get install git -y \
  && apt-get install python3.9-dev -y \
  && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
  && python3.9 get-pip.py \
  && pip3 install fschat fschat[model_worker,webui] torch torchvision torchaudio \
  && pip3 install accelerate  transformers[sentencepiece]==4.34.1 transformers==4.34.1 sentencepiece flash_attn bitsandbytes deepspeed
