import requests
import torch
from PIL import Image
from io import BytesIO

from diffusers import StableDiffusionImg2ImgPipeline

print("""
===
Source: https://huggingface.co/runwayml/stable-diffusion-v1-5

Model Description: This is a model that can be used to generate and modify images based on text prompts.
It is a Latent Diffusion Model (https://arxiv.org/abs/2112.10752) that uses a fixed, pretrained text encoder
(CLIP ViT-L/14, https://arxiv.org/abs/2103.00020) as suggested in the Imagen paper (https://arxiv.org/abs/2205.11487).
===
""")

model_id_or_path = "runwayml/stable-diffusion-v1-5"

image_url_init = "https://raw.githubusercontent.com/CompVis/stable-diffusion/main/assets/stable-samples/img2img/" \
                 "sketch-mountains-input.jpg"
image_path_init = "output/img2img_init.png"
image_path_generated = "output/img2img_generated.png"
prompt = "a fantasy landscape, trending on artstation"

device = "cpu"  # or cuda
print(f"[WARN] Running on {device} device")

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id_or_path)
if device == "cuda":
    pipe.torch_dtype = torch.float16
pipe = pipe.to(device)

print(f"Downloading init image from {image_url_init}...")
response = requests.get(image_url_init)
init_image = Image.open(BytesIO(response.content)).convert("RGB")
init_image = init_image.resize((768, 512))
init_image.save(image_path_init)
print(f"Saved init image to {image_path_init}")

print(f"Generating a new image from init image and prompt '{prompt}'...")
images = pipe(prompt=prompt, image=init_image, strength=0.75, guidance_scale=7.5).images
images[0].save(image_path_generated)
print(f"Saved generated image to {image_path_generated}")
