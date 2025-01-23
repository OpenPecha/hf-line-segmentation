import os
import json


def get_filter_out_ids(source_jsonl_path):
    filter_out_ids = set()
    with open(source_jsonl_path, "r") as source_file:
        for line in source_file:
            data = json.loads(line)
            id1 = data["line_id"].split("_")[0]
            filter_out_ids.add(id1)
    return filter_out_ids


def filter_target_jsonl(
    target_jsonl_path, filter_out_ids, output_jsonl_path, removed_ids
):
    target_data = []
    with open(target_jsonl_path, "r") as target_file:
        for line in target_file:
            data = json.loads(line)
            target_id = data["id"].split(".")[0]
            if target_id in filter_out_ids:
                removed_ids.append(target_id)
            else:
                target_data.append(data)
    with open(output_jsonl_path, "w") as output_file:
        for item in target_data:
            output_file.write(json.dumps(item) + "\n")


def process_jsonl_files(source_jsonl_path, target_dir, output_dir, removed_ids_file):
    filter_out_ids = get_filter_out_ids(source_jsonl_path)
    removed_ids = []
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".jsonl"):
                target_jsonl_path = os.path.join(root, file)
                target_output_path = os.path.join(
                    output_dir, os.path.relpath(target_jsonl_path, target_dir)
                )
                os.makedirs(os.path.dirname(target_output_path), exist_ok=True)
                filter_target_jsonl(
                    target_jsonl_path, filter_out_ids, target_output_path, removed_ids
                )

    save_removed_ids(removed_ids, removed_ids_file)


def save_removed_ids(removed_ids, removed_ids_file):
    with open(removed_ids_file, "w") as removed_ids_txt:
        for removed_id in removed_ids:
            removed_ids_txt.write(removed_id + "\n")


if __name__ == "__main__":
    source_jsonl_path = (
        "data/openpecha_data/output/monlam_data.jsonl" 
    )
    target_dir = "data/openpecha_data/annotation_source/4_LS_reviewed_annotation"
    output_dir = "data/openpecha_data/annotation_source/ls_reviewed_filtered_output"  
    removed_ids_file = "data/openpecha_data/annotation_source/ls_reviewed_filtered_output/removed_ids.txt"
    process_jsonl_files(source_jsonl_path, target_dir, output_dir, removed_ids_file)
