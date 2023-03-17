import requests
import torch
from PIL import Image
from diffusers import StableDiffusionDepth2ImgPipeline

print("""
===
Source: https://huggingface.co/stabilityai/stable-diffusion-2-depth

Model Description: This is a model that can be used to generate and modify images based on text prompts. It is a Latent
Diffusion Model (https://arxiv.org/abs/2112.10752) that uses a fixed, pretrained text encoder (OpenCLIP-ViT/H,
https://github.com/mlfoundations/open_clip).
===
""")

model_id_or_path = "stabilityai/stable-diffusion-2-depth"

image_url_init = "http://images.cocodataset.org/val2017/000000039769.jpg"
image_path_init = "output/img2img_depth_init.png"
image_path_generated = "output/img2img_depth_generated.png"
prompt = "two tigers"
negative_prompt = "bad, deformed, ugly, bad anatomy"

device = "cpu"  # or cuda
print(f"[WARN] Running on {device} device")

pipe = StableDiffusionDepth2ImgPipeline.from_pretrained(model_id_or_path)
if device == "cuda":
    pipe.torch_dtype = torch.float16
pipe = pipe.to(device)

print(f"Downloading init image from {image_url_init}...")
init_image = Image.open(requests.get(image_url_init, stream=True).raw)
init_image.save(image_path_init)
print(f"Saved init image to {image_path_init}")

print(f"Generating a new image from init image, prompt '{prompt}' and negative prompt '{negative_prompt}'...")
images = pipe(prompt=prompt, image=init_image, negative_prompt=negative_prompt, strength=0.7).images
images[0].save(image_path_generated)
print(f"Saved generated image to {image_path_generated}")
