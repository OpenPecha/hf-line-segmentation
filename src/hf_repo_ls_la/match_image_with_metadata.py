import os
import json
import glob
from multiprocessing import Pool, cpu_count


def extract_id_work_map(jsonl_dir):
    id_work_map = {}
    jsonl_formats = {}
    for jsonl_file in glob.glob(os.path.join(jsonl_dir, "*.jsonl")):
        # extract format from the josnl file name
        jsonl_name = os.path.basename(jsonl_file)
        format_name = jsonl_name.split("_")[1] if "_" in jsonl_name else ""
        jsonl_formats[jsonl_name] = format_name

        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                raw_id = data.get("id", "")
                id_value = raw_id.split(".")[0]
                image_url = data.get("image", "")
                work_id = ""
                if "Works" in image_url:
                    parts = image_url.split("/Works/")[1].split("/")
                    work_id = parts[1] if len(parts) > 1 else ""

                id_work_map[id_value] = {"work_id": work_id, "format": format_name}
    return id_work_map


def get_image_names(images_dir):
    return [os.path.basename(img) for img in glob.glob(os.path.join(images_dir, "*"))]


def process_image(image_name, id_work_map):
    image_id = image_name
    id_value = os.path.splitext(image_name)[0]
    bdrc_work_id = ""
    format_name = ""
    for jsonl_id, work_data in id_work_map.items():
        if jsonl_id in id_value:
            bdrc_work_id = work_data["work_id"]
            format_name = work_data["format"]
            break

    entry = {
        "image_id": image_id,
        "format": format_name,
        "BDRC_work_id": bdrc_work_id,
        "image_size_pixel": "512x512",
        "original_image": f"https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/mask_image_data/original_image/{image_id}",
        "mask_image": f"https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/mask_image_data/mask_image/{id_value}_mask.png"
    }
    return entry


def create_output_data(image_names, id_work_map):
    with Pool(cpu_count()) as pool:
        results = pool.starmap(process_image, [(image_name, id_work_map) for image_name in image_names])
    return results


def write_output_jsonl(output_data, output_jsonl):
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for entry in output_data:
            f.write(json.dumps(entry) + "\n")


def main(jsonl_dir, images_dir, output_jsonl):
    id_work_map = extract_id_work_map(jsonl_dir)
    image_names = get_image_names(images_dir)
    output_data = create_output_data(image_names, id_work_map)
    write_output_jsonl(output_data, output_jsonl)


jsonl_dir = "data/LS_reviewed_annotation"
images_dir = "/Users/tenkal/Downloads/line_segmentation/images"
output_jsonl = "data/output/erics_ls_data/mask_image_ls_data.jsonl"

if __name__ == "__main__":
    main(jsonl_dir, images_dir, output_jsonl)
