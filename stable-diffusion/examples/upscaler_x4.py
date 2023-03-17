import requests
import torch
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionUpscalePipeline

print("""
===
Source: https://huggingface.co/stabilityai/stable-diffusion-x4-upscaler

Model Description: This is a model that can be used to generate and modify images based on text prompts. It is a Latent
Diffusion Model (https://arxiv.org/abs/2112.10752) that uses a fixed, pretrained text encoder (OpenCLIP-ViT/H,
https://github.com/mlfoundations/open_clip).
===
""")

model_id_or_path = "stabilityai/stable-diffusion-x4-upscaler"

image_url_init = "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main/sd2-upscale/" \
                 "low_res_cat.png"
image_path_init = "output/upscaler_x4_init.png"
image_path_generated = "output/upscaler_x4_generated.png"
prompt = "a white cat"

device = "cpu"  # or cuda

pipe = StableDiffusionUpscalePipeline.from_pretrained(model_id_or_path)
if device == "cuda":
    pipe.torch_dtype = torch.float16
pipe = pipe.to(device)

print(f"Downloading init image from {image_url_init}...")
response = requests.get(image_url_init)
init_image = Image.open(BytesIO(response.content)).convert("RGB")
init_image = init_image.resize((128, 128))
init_image.save(image_path_init)
print(f"Saved init image to {image_path_init}")

print(f"Upscaling init image with prompt '{prompt}'...")
images = pipe(prompt=prompt, image=init_image).images
images[0].save(image_path_generated)
print(f"Saved generated image to {image_path_generated}")

