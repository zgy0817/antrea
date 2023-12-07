FROM nvidia/cuda:12.2.0-devel-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=CST-8

RUN apt-get update -y && apt-get install -y python3.9 python3.9-distutils curl \
  && apt-get install git -y \
  && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
  && python3.9 get-pip.py \
  && pip3 install fschat[model_worker,webui] fschat torch torchvision torchaudio \
  && pip3 install accelerate  transformers[sentencepiece] transformers sentencepiece flash_attn