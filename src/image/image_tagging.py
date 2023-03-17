import requests
from PIL import Image
from transformers import ViTImageProcessor, ViTForImageClassification

from image.colors import get_image_main_colors


def get_image_classes(raw_image, number_of_classes=10):
    image = Image.open(raw_image)
    processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
    model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    # Get the indices of the top 5 predicted classes
    top_5_idx = logits.topk(k=number_of_classes).indices.squeeze().tolist()
    # Print the top 5 predicted classes
    result = [model.config.id2label[idx] for idx in top_5_idx]
    print(f"Top {number_of_classes} predicted classes: \n{result}")
    return result


if __name__ == '__main__':
    url = 'http://images.cocodataset.org/val2017/000000039769.jpg'
    image = Image.open(requests.get(url, stream=True).raw)

    processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
    model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    # model predicts one of the 1000 ImageNet classes
    predicted_class_idx = logits.argmax(-1).item()
    print("Predicted class:", model.config.id2label[predicted_class_idx])

    number_of_classes = 5

    get_image_classes(requests.get(url, stream=True).raw, number_of_classes)

    get_image_main_colors(requests.get(url, stream=True).raw)
