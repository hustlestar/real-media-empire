import requests
from PIL import Image
from transformers import ViTImageProcessor, ViTForImageClassification

from image.colors import get_image_main_colors


def get_image_classes(raw_image=None, image_ndarray=None, number_of_classes=10):
    if raw_image is None and image_ndarray is None:
        raise
    if raw_image:
        image = Image.open(raw_image)
    else:
        image = Image.fromarray(image_ndarray)
    processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
    model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    # Get the indices of the top 5 predicted classes
    top_5_idx = logits.topk(k=number_of_classes).indices.squeeze().tolist()
    # Print the top 5 predicted classes
    result = [model.config.id2label[idx] for idx in top_5_idx]
    # print(f"Top {number_of_classes} predicted classes: \n{result}")
    return result


if __name__ == "__main__":
    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    image = Image.open(requests.get(url, stream=True).raw)

    processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
    model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")

    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    # model predicts one of the 1000 ImageNet classes
    # predicted_class_idx = logits.argmax(-1).item()
    # print("Predicted class:", model.config.id2label[predicted_class_idx])

    number_of_classes = 5

    # print(get_image_classes("E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\15088545.jpg", number_of_classes=number_of_classes))
    # print(get_image_classes("E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\12238773.jpg", number_of_classes=number_of_classes))
    # print(get_image_classes("E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\3588039.jpg", number_of_classes=number_of_classes))
    # print(get_image_classes("E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\1471295.jpg", number_of_classes=number_of_classes))
    # print(get_image_classes("E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\1126386.jpg", number_of_classes=number_of_classes))
    # print(get_image_classes("E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\12527622.jpg", number_of_classes=number_of_classes))
    print(get_image_classes("E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\13188540.jpg", number_of_classes=number_of_classes))

    # colors = get_image_main_colors(requests.get(url, stream=True).raw)
    # print(colors)
    # jpg = "E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\14821817.jpg"
    # get_image_classes(jpg, number_of_classes)
    # print(get_image_main_colors(jpg))
    # jpg = "E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\14532671.jpg"
    # get_image_classes(jpg, number_of_classes)
    # print(get_image_main_colors(jpg))
    # jpg = "E:\\MEDIA_GALLERY\\PHOTO\\landscape\\large2x\\14657304.jpg"
    # get_image_classes(jpg, number_of_classes)
    # print(get_image_main_colors(jpg))
