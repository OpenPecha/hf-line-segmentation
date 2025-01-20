import json
import os


def read_jsonl(jsonl_file):
    with open(jsonl_file, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]
    return data


def read_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def sort_entries_by_id(jsonl_data, json_data):
    sorted_data = {
        'test': [],
        'val': [],
        'train': []
    }

    test_ids = set(json_data.get('test', []))
    val_ids = set(json_data.get('val', []))
    train_ids = set(json_data.get('train', []))

    for entry in jsonl_data:
        image_id = entry.get('image_id')
        if image_id in test_ids:
            sorted_data['test'].append(entry)
        elif image_id in val_ids:
            sorted_data['val'].append(entry)
        elif image_id in train_ids:
            sorted_data['train'].append(entry)

    return sorted_data


def write_jsonl(sorted_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for key, entries in sorted_data.items():
        if entries:
            with open(f'{output_dir}/{key}.jsonl', 'w', encoding='utf-8') as file:
                for entry in entries:
                    file.write(json.dumps(entry) + '\n')


def main(jsonl_file, json_file, output_dir):
    jsonl_data = read_jsonl(jsonl_file)
    json_data = read_json(json_file)
    sorted_data = sort_entries_by_id(jsonl_data, json_data)
    write_jsonl(sorted_data, output_dir)


if __name__ == "__main__":
    jsonl_file = 'data/output/erics_LA_data/LA_mask_image_data.jsonl'
    json_file = 'data/la_split.json'
    output_dir = 'data/output/erics_LA_data/spilt_LA_data'
    main(jsonl_file, json_file, output_dir)
