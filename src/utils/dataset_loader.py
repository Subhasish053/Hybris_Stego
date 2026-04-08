import os

def load_image_paths(folder):

    images = []

    for file in os.listdir(folder):

        if file.endswith(".png") or file.endswith(".jpg"):

            images.append(os.path.join(folder, file))

    return images