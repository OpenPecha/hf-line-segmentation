import os
import json


def get_image_names(folder_path):
    return [img for img in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, img))]


def extract_image_names(base_dir):
    data = {}
    for folder in ['test', 'train', 'val']:
        folder_path = os.path.join(base_dir, folder, 'images')
        if os.path.isdir(folder_path):
            data[folder] = get_image_names(folder_path)
    return data


def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def main():
    base_dir = '/Users/tenkal/Downloads/layout_analysis'
    
    image_data = extract_image_names(base_dir)
    save_to_json(image_data, 'data/la_split.json')


if __name__ == "__main__":
    main()
