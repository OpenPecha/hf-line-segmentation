import json
from src.openpecha_ls_la.jsonl_parser import (
    extract_bdrc_work_id,
    process_jsonl_file,
    process_all_jsonl_files,
)


def test_extract_bdrc_work_id():
    assert (
        extract_bdrc_work_id(
            "https://s3.amazonaws.com/image-processing.openpecha/Works/fe/W1AC364/images-web/W1AC364-I2PD17989/I2PD179890017.jpg_2000x700.jpg"
        )
        == "W1AC364"
    )
    assert (
        extract_bdrc_work_id(
            "https://s3.amazonaws.com/image-processing.openpecha/Works/fe/W1AC365/images-web/W1AC364-I2PD17989/I2PD179890017.jpg_2000x700.jpg"
        )
        == "W1AC365"
    )


def test_process_jsonl_file(tmp_path):
    jsonl_content = """
    {"id": "I2PD179890017.jpg_2000x700.jpg", "image": "https://s3.amazonaws.com/image-processing.openpecha/Works/fe/W1AC364/images-web/W1AC364-I2PD17989/I2PD179890017.jpg_2000x700.jpg", "spans": [{"label": "Line", "points": [[0, 0], [1, 1]]}]}
    """
    jsonl_file = tmp_path / "ls_modern_00_review.jsonl"
    jsonl_file.write_text(jsonl_content.strip())

    result = process_jsonl_file(jsonl_file)
    assert result[0]["line_id"] == "I2PD179890017_1"
    assert result[0]["line_coordinates"] == [[0.0, 0.0], [1.0, 1.0]]
    assert result[0]["source_image"] == "I2PD179890017.jpg"
    assert result[0]["image_size"] == "2000x700"
    assert result[0]["format"] == "modern"
    assert result[0]["bdrc_work_id"] == "W1AC364"
    assert (
        result[0]["image_url"]
        == "https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/coordinate_image_data/source_image/prodigy_method/I2PD179890017.jpg"
    )
    assert result[0]["method"] == "Prodigy"


def test_process_all_jsonl_files(tmp_path):
    jsonl_content1 = """
    {"id": "I2PD179890017.jpg_2000x700.jpg", "image": "ttps://s3.amazonaws.com/image-processing.openpecha/Works/fe/W1AC364/images-web/W1AC364-I2PD17989/I2PD179890017.jpg_2000x700.jpg", "spans": [{"label": "Line", "points": [[0, 0], [1, 1]]}]}
    """
    jsonl_content2 = """
    {"id": "I2PD179860227.jpg_2000x700.jpg", "image": "https://s3.amazonaws.com/image-processing.openpecha/Works/fe/W1AC364/images-web/W1AC364-I2PD17986/I2PD179860227.jpg_2000x700.jpg", "spans": [{"label": "Line", "points": [[2, 2], [3, 3]]}]}
    """
    jsonl_file1 = tmp_path / "ls_modern_00_review.jsonl"
    jsonl_file2 = tmp_path / "ls_pering_00_review.jsonl"
    jsonl_file1.write_text(jsonl_content1.strip())
    jsonl_file2.write_text(jsonl_content2.strip())

    output_file = tmp_path / "output.jsonl"
    process_all_jsonl_files(tmp_path, output_file)

    with open(output_file, "r") as f:
        lines = f.readlines()
        assert len(lines) == 2
        result1 = json.loads(lines[0])
        result2 = json.loads(lines[1])
        assert result1["line_id"] == "I2PD179890017_1"
        assert result2["line_id"] == "I2PD179860227_1"
