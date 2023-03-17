
if __name__ == '__main__':
    prompt = "youtube thumbnail for the video with title 4 best advices for your morning"
    # from diffusers import StableDiffusionPipeline
    # import torch
    #
    # model_id = "runwayml/stable-diffusion-v1-5"
    # pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    # pipe = pipe.to("cuda")
    #
    # image = pipe(prompt).images[0]
    #
    # image.save("1.png")

    import torch
    from diffusers import StableDiffusionPipeline

    model_id = "CompVis/stable-diffusion-v1-4"
    # device = "cuda"


    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    # pipe = pipe.to(device)

    prompt = "a photo of an astronaut riding a horse on mars"
    image = pipe(prompt).images[0]

    image.save("astronaut_rides_horse.png")