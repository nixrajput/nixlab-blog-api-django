import os
from cv2 import imread


def is_image_aspect_ratio_valid(img_url):
    img = imread(img_url)
    dimension = tuple(img.shape[1::-1])
    print("dimensions: " + str(dimension))
    aspect_ratio = dimension[0] / dimension[1]
    print("aspect_ratio: " + str(aspect_ratio))
    if aspect_ratio < 1:
        return False
    return True


def is_image_size_valid(img_url, mb_limit):
    image_size = os.path.getsize(img_url)
    print("image_size: " + str(image_size))
    print("max_limit: " + str(mb_limit))
    if image_size > mb_limit:
        return False
    return True
