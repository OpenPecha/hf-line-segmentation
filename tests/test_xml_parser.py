import os
import json
import pytest
from src.openpecha_ls_la.xml_parser import (
    extract_image_info,
    extract_text_lines,
    process_xml_file,
    process_directory,
)

import xml.etree.ElementTree as ET


@pytest.fixture
def setup_test_environment(tmp_path):
    namespace = {
        "ns": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
    }
    test_xml = """<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">
        <Page imageFilename="test_image.jpg" imageWidth="1000" imageHeight="2000">
            <TextRegion custom="readingOrder">
                <TextLine>
                    <Coords points="10,10 20,20 30,30"/>
                </TextLine>
            </TextRegion>
        </Page>
    </PcGts>"""
    test_dir = tmp_path / "test_data"
    test_file = test_dir / "test.xml"
    test_dir.mkdir()
    test_file.write_text(test_xml)
    return namespace, test_xml, test_dir, test_file


def test_extract_image_info(setup_test_environment):
    namespace, test_xml, _, _ = setup_test_environment
    root = ET.fromstring(test_xml)
    page = root.find("ns:Page", namespace)
    source_image, image_size, image_url = extract_image_info(page, namespace)
    assert source_image == "test_image.jpg"
    assert image_size == "1000x2000"
    assert (
        image_url
        == "https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/coordinate_image_data/source_image/esukhia_transkribus_method/test_image.jpg"
    )


def test_extract_text_lines(setup_test_environment):
    namespace, test_xml, _, _ = setup_test_environment
    root = ET.fromstring(test_xml)
    page = root.find("ns:Page", namespace)
    text_regions = page.findall("ns:TextRegion", namespace)
    source_image = "test_image.jpg"
    line_data = extract_text_lines(text_regions, namespace, source_image)
    assert len(line_data) == 1
    assert line_data[0]["line_id"] == "test_image_1"
    assert line_data[0]["line_coordinates"] == [
        [10.0, 10.0],
        [20.0, 20.0],
        [30.0, 30.0],
    ]


def test_process_xml_file(setup_test_environment):
    namespace, _, _, test_file = setup_test_environment
    line_data = process_xml_file(test_file, namespace)
    assert len(line_data) == 1
    assert line_data[0]["source_image"] == "test_image.jpg"
    assert line_data[0]["image_size"] == "1000x2000"
    assert (
        line_data[0]["image_url"]
        == "https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/coordinate_image_data/source_image/esukhia_transkribus_method/test_image.jpg"
    )
    assert line_data[0]["method"] == "Transkribus"


def test_process_directory(setup_test_environment, tmp_path):
    namespace, _, test_dir, _ = setup_test_environment
    output_file = tmp_path / "output.jsonl"
    process_directory(test_dir, output_file)
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["source_image"] == "test_image.jpg"
    assert data["image_size"] == "1000x2000"
    assert (
        data["image_url"]
        == "https://s3.amazonaws.com/monlam.ai.ocr/LineSegmentation/coordinate_image_data/source_image/esukhia_transkribus_method/test_image.jpg"
    )
    assert data["method"] == "Transkribus"
