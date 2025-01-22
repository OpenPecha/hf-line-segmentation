import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


def find_page_folders(root_dir):
    page_folders = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == "page":
            page_folders.append(dirpath)
    return page_folders


def collect_xml_files(page_folders):
    xml_files = []
    for folder in page_folders:
        for file in os.listdir(folder):
            if file.endswith(".xml"):
                xml_files.append(os.path.join(folder, file))
    return xml_files


def rename_update_filter_xml(xml_files, output_without_ann, output_with_ann_and_text_equiv, output_with_ann_without_text_equiv):
    file_counts = defaultdict(int)
    renamed_files = defaultdict(list)
    namespace = {'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}

    for xml_file in xml_files:
        original_name = os.path.basename(xml_file)
        file_counts[original_name] += 1
        count = file_counts[original_name]
        name, ext = os.path.splitext(original_name)
        new_name = f"{name}_{count:03d}.xml"

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            page_tag = root.find(".//ns:Page", namespaces=namespace)
            if page_tag is None:
                logging.warning(f"No <Page> tag found in {xml_file}. Skipping file.")
                continue

            if 'imageFilename' in page_tag.attrib:
                page_tag.set('imageFilename', f"{new_name.replace('.xml', '.jpg')}")

            # ckeck for <TextRegion> in the xml
            text_region_tag = root.findall(".//ns:TextRegion", namespaces=namespace)
            # check for <TextEquiv> in the xml
            if text_region_tag:
                text_equiv_tag = root.findall(".//ns:TextEquiv", namespaces=namespace)
                if text_equiv_tag:
                    output_path = os.path.join(output_with_ann_and_text_equiv, new_name)
                else:
                    output_path = os.path.join(output_with_ann_without_text_equiv, new_name)
            else:
                output_path = os.path.join(output_without_ann, new_name)

            tree.write(output_path, encoding="utf-8", xml_declaration=True)
            renamed_files[original_name].append(new_name)

        except ET.ParseError as e:
            logging.error(f"Error parsing {xml_file}: {e}")

    return renamed_files


def main(input_dir, output_without_ann, output_with_ann_and_text_equiv, output_with_ann_without_text_equiv):
    os.makedirs(output_without_ann, exist_ok=True)
    os.makedirs(output_with_ann_and_text_equiv, exist_ok=True)
    os.makedirs(output_with_ann_without_text_equiv, exist_ok=True)

    page_folders = find_page_folders(input_dir)
    xml_files = collect_xml_files(page_folders)
    rename_update_filter_xml(xml_files, output_without_ann, output_with_ann_and_text_equiv,
                             output_with_ann_without_text_equiv)


if __name__ == "__main__":
    input_dir = "data/openpecha_data/annotation_source/3_the_esukhia_data"
    output_without_ann = "data/openpecha_data/annotation_source/updated_esukhia_data/without_annotation"
    output_with_ann_and_text_equiv = "data/openpecha_data/annotation_source/updated_esukhia_data/with_annotation_and_full_line"
    output_with_ann_without_text_equiv = "data/openpecha_data/annotation_source/updated_esukhia_data/with_annotation_and_only_head"
    main(input_dir, output_without_ann, output_with_ann_and_text_equiv, output_with_ann_without_text_equiv)
