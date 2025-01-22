import os
import requests
import logging
from xml.etree import ElementTree as ET
from multiprocessing import Pool


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        logger.info(f"Downloaded: {save_path}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")


def parse_xml_for_images(xml_path, output_dir):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        ns = {"ns0": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}

        metadata = root.find(".//ns0:TranskribusMetadata", ns)
        page = root.find(".//ns0:Page", ns)

        if metadata is not None and page is not None:
            img_url = metadata.attrib.get("imgUrl", "").replace("&amp;", "&")
            image_filename = page.attrib.get("imageFilename", "unknown.jpg")

            if img_url:
                save_path = os.path.join(output_dir, image_filename)
                download_image(img_url, save_path)
            else:
                logger.warning(f"No 'imgUrl' found in {xml_path}")
        else:
            logger.warning(f"No Metadata or Page element found in {xml_path}")
    except ET.ParseError as e:
        logger.error(f"Failed to parse {xml_path}: {e}")


def traverse_and_download_images(root_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    xml_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".xml"):
                xml_files.append(os.path.join(dirpath, filename))

    with Pool() as pool:
        pool.starmap(parse_xml_for_images, [(xml_path, output_dir) for xml_path in xml_files])


def main():
    root_directory = "data/openpecha_data/annotation_source/updated_esukhia_data/with_annotation_and_full_line"
    output_directory = "data/openpecha_data/images/esukhia_data/with_annotation_and_full_line"
    traverse_and_download_images(root_directory, output_directory)


if __name__ == "__main__":
    main()
