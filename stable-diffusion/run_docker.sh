#!/bin/bash

docker build . -t stable-diffusion:latest
mkdir -p output

echo "Run the desired example in Docker shell, eg.: '> python examples/stable_diffusion.py'"
echo "Then check the outputs in ./output dir"

docker run -it --rm --name stable-diffusion \
  -v "$PWD":/usr/stable-diffusion \
  -w /usr/stable-diffusion \
  stable-diffusion:latest \
  bash
