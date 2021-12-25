from io import StringIO, open

import pytest

import pwk


@pytest.mark.parametrize(
    "filename,expression", [("test", "_1 * 2, _2.upper(), _3 + '?'")]
)
@pytest.mark.parametrize("input_format", ["csv", "tsv"])
@pytest.mark.parametrize("output_format", ["csv", "tsv"])
def test_files(filename, expression, input_format, output_format):
    input_filename = f"test_files/{filename}.{input_format}"
    output_filename = f"test_files/{filename}_output.{output_format}"
    output = StringIO()
    pwk.main([expression, input_filename, "-o", output_format], output)
    with open(output_filename, newline="") as output_file:
        expected_output = output_file.read()
    assert output.getvalue() == expected_output
