from io import StringIO, open

import pytest

import pwk


@pytest.mark.parametrize("input_format", ["csv", "tsv"])
@pytest.mark.parametrize("output_format", ["csv", "tsv"])
def test_file_formats(input_format, output_format):
    input_filename = f"test_files/test.{input_format}"
    output_filename = f"test_files/test_output.{output_format}"
    output = StringIO()
    pwk.main(
        ["_1 * 2, _2.upper(), _3 + '?'", input_filename, "-o", output_format], output
    )
    with open(output_filename, newline="") as output_file:
        expected_output = output_file.read()
    assert output.getvalue() == expected_output


def test_aggregate():
    output = StringIO()
    pwk.main(["-a", "sum(_2)", "test_files/aggregate.csv", "-o", "csv"], output)
    with open("test_files/aggregate_output.csv", newline="") as output_file:
        expected_output = output_file.read()
    assert output.getvalue() == expected_output


def test_header():
    output = StringIO()
    pwk.main(
        [
            "_['first name'] + ' ' + _['last_name'], _['phone-number']",
            "test_files/header.csv",
            "-H",
            "-s",
            "-o",
            "csv",
        ],
        output,
    )
    with open("test_files/header_output.csv", newline="") as output_file:
        expected_output = output_file.read()
    assert output.getvalue() == expected_output

    # Aggregation
    output = StringIO()
    pwk.main(
        ["sum(_['phone-number'])", "test_files/header.csv", "-H", "-a", "-o", "csv"],
        output,
    )
    assert output.getvalue() == "1111111110\r\n"
