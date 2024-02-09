FROM nvidia/cuda:12.2.0-devel-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=CST-8
ENV WANDB_MODE=disabled

RUN apt-get update -y && apt-get install -y python3.9 python3.9-distutils curl \
  && apt-get install git -y \
  && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
  && python3.9 get-pip.py \
  && pip3 install packaging \
  && pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
  && pip3 install accelerate==0.22.0 \
  && pip3 install transformers[sentencepiece]==4.34.1 sentencepiece flash_attn\
  && pip3 install "fschat[train]" 
 