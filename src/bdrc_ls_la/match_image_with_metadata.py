import os
import json
import glob
from multiprocessing import Pool, cpu_count


def extract_id_work(jsonl_dir):
    '''extract id, work_id and format from the jsonl files'''
    id_work = {}
    jsonl_formats = {}
    for jsonl_file in glob.glob(os.path.join(jsonl_dir, "*.jsonl")):
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

                id_work[id_value] = {"work_id": work_id, "format": format_name}
    return id_work


def get_image_names(images_dir):
    image_names = []
    for root, dirs, files in os.walk(images_dir):
        if os.path.basename(root) == "images":
            image_names.extend([os.path.join(root, file) for file in files])
    return image_names


def process_image(image_path, id_work):
    image_name = os.path.basename(image_path)
    id_value = os.path.splitext(image_name)[0]
    bdrc_work_id = ""
    format_name = ""
    for jsonl_id, work_data in id_work.items():
        if jsonl_id in id_value:
            bdrc_work_id = work_data["work_id"]
            format_name = work_data["format"]
            break

    entry = {
        "image_id": image_name,
        "format": format_name,
        "BDRC_work_id": bdrc_work_id,
        "image_size_pixel": "512x512",
        "original_image": f"https://s3.amazonaws.com/monlam.ai.ocr/LayoutAnalysis/mask_image_data/original_image/{image_name}",
        "mask_image": f"https://s3.amazonaws.com/monlam.ai.ocr/LayoutAnalysis/mask_image_data/mask_image/{id_value}_mask.png"
    }
    return entry


def create_output_data(image_paths, id_work):
    with Pool(cpu_count()) as pool:
        results = pool.starmap(process_image, [(image_path, id_work) for image_path in image_paths])
    return results


def write_output_jsonl(output_data, output_jsonl):
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for entry in output_data:
            f.write(json.dumps(entry) + "\n")


def main(jsonl_dir, images_dir, output_jsonl):
    id_work = extract_id_work(jsonl_dir)
    image_paths = get_image_names(images_dir)
    output_data = create_output_data(image_paths, id_work)
    write_output_jsonl(output_data, output_jsonl)


jsonl_dir = "data/LS_reviewed_annotation"
images_dir = "/Users/tenkal/Downloads/layout_analysis"
output_jsonl = "data/output/erics_LA_data/LA_mask_image_data.jsonl"

if __name__ == "__main__":
    main(jsonl_dir, images_dir, output_jsonl)
