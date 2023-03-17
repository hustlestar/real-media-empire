import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, EulerDiscreteScheduler

print("""
===
Source: https://huggingface.co/stabilityai

Example model IDs:
- stabilityai/stable-diffusion-2-1-base - latest base stable diffusion original model
- stabilityai/stable-diffusion-2-1 - latest stable diffusion original model
- stalkeryga/f222 - nude girls ;)
===
""")

# model_id_or_path = "stabilityai/stable-diffusion-2-1-base"
model_id_or_path = "stabilityai/stable-diffusion-2-1"
# model_id_or_path = "stalkeryga/f222"

image_path_generated = f"output/stable_diffusion_{model_id_or_path.split('/')[1]}_generated.png"
prompt = "a photo of an astronaut riding a horse on mars"

device = "cpu"  # or cuda
print(f"[WARN] Running on {device} device")

pipe = StableDiffusionPipeline.from_pretrained(model_id_or_path)
if device == "cuda":
    pipe.torch_dtype = torch.float16
if model_id_or_path == "stabilityai/stable-diffusion-2-1":
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
if model_id_or_path == "stable-diffusion-2-1-base":
    pipe.scheduler = EulerDiscreteScheduler.from_pretrained(pipe.scheduler.config)

# Disable safety check for explicit content.
pipe.safety_checker = lambda images, clip_input: (images, False)

pipe = pipe.to(device)

print(f"Generating a new image from init image, prompt '{prompt}'...")
images = pipe(
    prompt=prompt,
    # num_inference_steps=50,  # Use to control inference speed and quality tradeoff.
).images
images[0].save(image_path_generated)
print(f"Saved generated image to {image_path_generated}")
