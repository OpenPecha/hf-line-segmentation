import os
import json
import xml.etree.ElementTree as ET


def extract_image_info(page, namespace):
    source_image = page.attrib.get("imageFilename")
    image_width = page.attrib.get("imageWidth")
    image_height = page.attrib.get("imageHeight")
    image_size = f"{image_width}x{image_height}"
    image_url = f"https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/coordinate_image_data/source_image/esukhia_transkribus_method/{source_image}"
    return source_image, image_size, image_url


def extract_text_lines(text_regions, namespace, source_image):
    line_data = []
    line_count = 1

    for region in text_regions:
        custom_attr = region.attrib.get("custom", "")
        if "readingOrder" in custom_attr or "type:paragraph" in custom_attr:
            text_lines = region.findall("ns:TextLine", namespace)
            for line in text_lines:
                line_id = f"{os.path.splitext(source_image)[0]}_{line_count}"
                coords = line.find("ns:Coords", namespace)
                if coords is not None:
                    points = coords.attrib.get("points", "")
                    point_list = [
                        [float(x), float(y)]
                        for x, y in (point.split(",") for point in points.split())
                    ]
                    line_data.append(
                        {"line_id": line_id, "line_coordinates": point_list}
                    )
                    line_count += 1

    return line_data


def process_xml_file(file_path, namespace):
    tree = ET.parse(file_path)
    root_element = tree.getroot()

    page = root_element.find("ns:Page", namespace)
    if page is None:
        return []
    source_image, image_size, image_url = extract_image_info(page, namespace)
    text_regions = page.findall("ns:TextRegion", namespace)
    line_data = extract_text_lines(text_regions, namespace, source_image)

    for line in line_data:
        line.update(
            {
                "source_image": source_image,
                "image_size": image_size,
                "image_url": image_url,
                "method": "Transkribus",
            }
        )

    return line_data


def process_directory(input_dir, output_file):
    namespace = {
        "ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
    }
    all_data = []

    xml_files_found = False

    for root, dirs, files in os.walk(input_dir):
        if "page" not in root:
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root, file)
                    data = process_xml_file(file_path, namespace)
                    all_data.extend(data)
                    xml_files_found = True

    if not xml_files_found:
        for root, dirs, files in os.walk(input_dir):
            if "page" in root:
                for file in files:
                    if file.endswith(".xml"):
                        file_path = os.path.join(root, file)
                        data = process_xml_file(file_path, namespace)
                        all_data.extend(data)

    if all_data:
        with open(output_file, "w", encoding="utf-8") as f:
            for entry in all_data:
                f.write(json.dumps(entry) + "\n")
    else:
        print("No data to write.")


def main():
    input_directory = "data/openpecha_data/annotation_source/updated_esukhia_data/with_annotation_and_only_head"
    output_file = "data/openpecha_data/esukhia_output/without_superscript_subscript.jsonl"

    process_directory(input_directory, output_file)
    print(f"Data has been successfully written to {output_file}")


if __name__ == "__main__":
    main()
