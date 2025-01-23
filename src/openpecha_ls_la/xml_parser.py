import os
import json
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from collections import defaultdict


def load_jsonl_data(jsonl_dir):
    data_dict = defaultdict(list)
    for root, _, files in os.walk(jsonl_dir):
        for file in files:
            if file.endswith(".jsonl"):
                jsonl_file = os.path.join(root, file)
                with open(jsonl_file, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        id2 = data.get("id", "").split(".")[0]
                        image_url = data.get("image", "")
                        format_value = file.split("_")[1] if "_" in file else "unknown"
                        bdrc_work_id = (
                            image_url.split("/Works/")[1].split("/")[1]
                            if "/Works/" in image_url
                            else "unknown"
                        )
                        data_dict[id2].append(
                            {
                                "format": format_value,
                                "bdrc_work_id": bdrc_work_id,
                            }
                        )
    return data_dict


def extract_image_info(page, namespace):
    source_image = page.attrib.get("imageFilename")
    image_width = page.attrib.get("imageWidth")
    image_height = page.attrib.get("imageHeight")
    image_size = f"{image_width}x{image_height}"
    image_url = f"https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/coordinate_image_data/source_image/{source_image}"
    return source_image, image_size, image_url


def extract_text_lines(text_regions, namespace, source_image):
    line_data = []
    line_count = 1

    for region in text_regions:
        custom_attr = region.attrib.get("custom", "")
        coords = region.find("ns:Coords", namespace)

        if coords is not None:
            points = coords.attrib.get("points", "")
            point_list = [
                [int(point.split(",")[0]), int(point.split(",")[1])]
                for point in points.split()
            ]

            if "type:paragraph" in custom_attr:
                text_lines = region.findall("ns:TextLine", namespace)
                for line in text_lines:
                    line_id = f"{os.path.splitext(source_image)[0]}_{line_count}"
                    line_coords = line.find("ns:Coords", namespace)
                    if line_coords is not None:
                        points = line_coords.attrib.get("points", "")
                        point_list = [
                            [int(point.split(",")[0]), int(point.split(",")[1])]
                            for point in points.split()
                        ]
                        line_data.append(
                            {"line_id": line_id, "line_coordinates": point_list}
                        )
                        line_count += 1
            else:
                line_id = f"{os.path.splitext(source_image)[0]}_{line_count}"
                line_data.append({"line_id": line_id, "line_coordinates": point_list})
                line_count += 1
    return line_data


def find_format_and_bdrc_work_id(data_dict, id1):
    if id1 in data_dict:
        return data_dict[id1][0]["format"], data_dict[id1][0]["bdrc_work_id"]
    return "unknown", "unknown"


def process_xml_file(file_path, namespace, data_dict):
    tree = ET.parse(file_path)
    root_element = tree.getroot()

    page = root_element.find("ns:Page", namespace)
    if page is None:
        return []
    source_image, image_size, image_url = extract_image_info(page, namespace)
    id1 = os.path.splitext(source_image)[0]
    format_value, bdrc_work_id = find_format_and_bdrc_work_id(data_dict, id1)

    text_regions = page.findall("ns:TextRegion", namespace)
    line_data = extract_text_lines(text_regions, namespace, source_image)
    for line in line_data:
        line.update(
            {
                "source_image": source_image,
                "image_size": image_size,
                "format": format_value,
                "bdrc_work_id": bdrc_work_id,
                "image_url": image_url,
                "method": "Transkribus",
            }
        )
    return line_data


def process_directory(input_dir, jsonl_dir, output_file):
    namespace = {
        "ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
    }
    all_data = []
    data_dict = load_jsonl_data(jsonl_dir)
    with Pool() as pool:
        tasks = []
        for root, dirs, files in os.walk(input_dir):
            if "page" in root:
                for file in files:
                    if file.endswith(".xml"):
                        file_path = os.path.join(root, file)
                        tasks.append(file_path)

        results = pool.starmap(
            process_xml_file, [(task, namespace, data_dict) for task in tasks]
        )
        for result in results:
            all_data.extend(result)

    with open(output_file, "w", encoding="utf-8") as f:
        for entry in all_data:
            f.write(json.dumps(entry) + "\n")

def main():
    input_directory = "data/openpecha_data/annotation_source/1_monlam_data"
    jsonl_directory = "data/openpecha_data/annotation_source/jsonl_reviewed_annotation"
    output_file = "data/openpecha_data/output/monlam_data.jsonl"

    process_directory(input_directory, jsonl_directory, output_file)


if __name__ == "__main__":
    main()
