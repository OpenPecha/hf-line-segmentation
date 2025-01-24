import os
import json


def extract_bdrc_work_id(image_url):
    try:
        return image_url.split("/Works/")[1].split("/")[1]
    except IndexError:
        return None


def process_jsonl_file(file_path):
    line_data = []
    with open(file_path, "r") as file:
        for line in file:
            try:
                json_obj = json.loads(line.strip())
                source_image = json_obj.get("id", "").split(".")[0] + ".jpg"
                image_size = json_obj.get("id", "").split(".")[1].split("_")[1]
                image_format = os.path.basename(file_path).split("_")[1]
                bdrc_work_id = extract_bdrc_work_id(json_obj.get("image", ""))

                line_count = 0
                for span in json_obj.get("spans", []):
                    if span.get("label") == "Line":
                        line_count += 1
                        line_id = f"{source_image.split('.')[0]}_{line_count}"
                        line_coordinates = span.get("points", [])
                        # Convert coordinates to float
                        line_coordinates = [
                            [float(coord[0]), float(coord[1])]
                            for coord in line_coordinates
                        ]
                        image_url = f"https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/coordinate_image_data/source_image/prodigy_method/{source_image}"

                        line_data.append(
                            {
                                "line_id": line_id,
                                "line_coordinates": line_coordinates,
                                "source_image": source_image,
                                "image_size": image_size,
                                "format": image_format,
                                "bdrc_work_id": bdrc_work_id,
                                "image_url": image_url,
                                "method": "Prodigy",
                            }
                        )

            except (json.JSONDecodeError, KeyError, IndexError):
                continue
    return line_data


def process_all_jsonl_files(directory_path, output_file):
    combined_data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".jsonl"):
            file_path = os.path.join(directory_path, filename)
            combined_data.extend(process_jsonl_file(file_path))

    with open(output_file, "w") as output:
        for entry in combined_data:
            output.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    directory_path = "data/openpecha_data/annotation_source/jsonl_filtered_output"
    output_file = "data/openpecha_data/output/prodigy_monlam_data.jsonl"

    process_all_jsonl_files(directory_path, output_file)
