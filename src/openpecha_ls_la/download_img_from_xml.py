import os
import requests
from xml.etree import ElementTree as ET
from concurrent.futures import ProcessPoolExecutor


def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")


def parse_xml_for_images(xml_path, output_dir):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {"ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
        metadata = root.find("ns:Metadata/ns:TranskribusMetadata", ns)
        page = root.find("ns:Page", ns)

        if metadata is not None and "imgUrl" in metadata.attrib and page is not None:
            img_url = metadata.attrib["imgUrl"].replace("&amp;", "&")
            image_filename = page.attrib.get("imageFilename", "unknown.jpg")

            save_path = os.path.join(output_dir, image_filename)
            download_image(img_url, save_path)
    except ET.ParseError as e:
        print(f"Failed to parse {xml_path}: {e}")


def process_page_folder(args):
    dirpath, output_dir = args
    for file in os.listdir(dirpath):
        if file.endswith(".xml"):
            xml_path = os.path.join(dirpath, file)
            parse_xml_for_images(xml_path, output_dir)


def traverse_and_download_images(root_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    page_folders = [
        (os.path.join(dirpath, dir_name), output_dir)
        for dirpath, dirnames, _ in os.walk(root_dir)
        for dir_name in dirnames
        if dir_name == "page"
    ]

    with ProcessPoolExecutor() as executor:
        executor.map(process_page_folder, page_folders)


def main():
    root_directory = "data/openpecha_data/annotation_source/3_the_esukhia_data"
    output_directory = "data/openpecha_data/images/esukhia_data"
    traverse_and_download_images(root_directory, output_directory)


if __name__ == "__main__":
    main()
