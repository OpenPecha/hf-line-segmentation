import os
import json
import xml.etree.ElementTree as ET


def extract_image_info(page, namespace):
    source_image = page.attrib.get("imageFilename")
    image_width = page.attrib.get("imageWidth")
    image_height = page.attrib.get("imageHeight")
    image_size = f"{image_width}x{image_height}"
    image_url = f"https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/coordinate_image_data/source_image/{source_image}"
    return source_image, image_size, image_url


def extract_text_lines(text_regions, namespace, source_image):
    """
    Extract lines and coordinates from TextRegions. If the type attribute is missing,
    use the TextRegion's coordinates directly.
    """
    line_data = []
    line_count = 1

    for region in text_regions:
        custom_attr = region.attrib.get("custom", "")
        coords = region.find("ns:Coords", namespace)

        if coords is not None:
            points = coords.attrib.get("points", "")

            if "type:paragraph" in custom_attr:

                text_lines = region.findall("ns:TextLine", namespace)
                for line in text_lines:
                    line_id = f"{os.path.splitext(source_image)[0]}_{line_count}"
                    line_coords = line.find("ns:Coords", namespace)
                    if line_coords is not None:
                        points = line_coords.attrib.get("points", "")
                        line_data.append(
                            {"line_id": line_id, "line_coordinates": points}
                        )
                        line_count += 1
            else:

                line_id = f"{os.path.splitext(source_image)[0]}_{line_count}"
                line_data.append({"line_id": line_id, "line_coordinates": points})
                line_count += 1

    return line_data


def find_format_and_bdrc_work_id(jsonl_dir, id1):
    for root, _, files in os.walk(jsonl_dir):
        for file in files:
            if file.endswith(".jsonl"):
                jsonl_file = os.path.join(root, file)
                with open(jsonl_file, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        id2 = data.get("id", "").split(".")[0]
                        if id1 == id2:
                            format_value = (
                                file.split("_")[1] if "_" in file else "unknown"
                            )
                            image_url = data.get("image", "")
                            bdrc_work_id = (
                                image_url.split("/Works/")[1].split("/")[1]
                                if "/Works/" in image_url
                                else "unknown"
                            )
                            return format_value, bdrc_work_id
    return "unknown", "unknown"


def process_xml_file(file_path, namespace, jsonl_dir):
    tree = ET.parse(file_path)
    root_element = tree.getroot()

    page = root_element.find("ns:Page", namespace)
    if page is None:
        return []
    source_image, image_size, image_url = extract_image_info(page, namespace)
    id1 = os.path.splitext(source_image)[0]
    format_value, bdrc_work_id = find_format_and_bdrc_work_id(jsonl_dir, id1)

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
                "method": "Transkribus"
            }
        )

    return line_data


def process_directory(input_dir, jsonl_dir, output_file):
    namespace = {
        "ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
    }
    all_data = []

    for root, dirs, files in os.walk(input_dir):
        if "page" in root:
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    data = process_xml_file(file_path, namespace, jsonl_dir)
                    all_data.extend(data)

    with open(output_file, "w", encoding="utf-8") as f:
        for entry in all_data:
            f.write(json.dumps(entry) + "\n")


def main():
    input_directory = "data/openpecha_data/annotation_source/2_second_monlam_data"
    jsonl_directory = "data/openpecha_data/annotation_source/jsonl_reviewed_annotation"
    output_file = "data/openpecha_data/output/second_monlam_data.jsonl"

    process_directory(input_directory, jsonl_directory, output_file)


if __name__ == "__main__":
    main()
