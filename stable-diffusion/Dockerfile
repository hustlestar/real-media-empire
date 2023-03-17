FROM python:3.7

RUN apt-get update -y
RUN pip install --upgrade pip wheel setuptools

RUN pip install diffusers transformers accelerate scipy safetensors

RUN mkdir -p /usr/stable-diffusion

WORKDIR /usr/stable-diffusion
