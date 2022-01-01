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


def test_regex():
    # Using capture groups
    output = StringIO()
    pwk.main(
        [
            "fullmatch(r'(.+?)://(?:.+?@)?(.+?)(?::.+)?(?:/.+)?', _1)",
            "test_files/regex.txt",
            "-o",
            "csv",
        ],
        output,
    )
    with open("test_files/regex_output.csv", newline="") as output_file:
        expected_output = output_file.read()
    assert output.getvalue() == expected_output

    # Without using capture groups
    output = StringIO()
    pwk.main(
        [
            "match(r'[^:]+', _1), search(r'\\w+\\.\\w+', _1)",
            "test_files/regex.txt",
            "-o",
            "csv",
        ],
        output,
    )
    with open("test_files/regex_output.csv", newline="") as output_file:
        expected_output = output_file.read()
    assert output.getvalue() == expected_output


def test_iterable():
    output = StringIO()
    pwk.main(
        [
            "tuple(_1), list(enumerate(_2))",
            "test_files/iterable.csv",
            "-s",
            "-o",
            "csv",
        ],
        output,
    )
    with open("test_files/iterable_output.csv", newline="") as output_file:
        expected_output = output_file.read()
    assert output.getvalue() == expected_output


def test_filter():
    output = StringIO()
    pwk.main(
        [
            "_0 if _n % 2 == 1 else None",
            "test_files/filter.csv",
            "-o",
            "csv",
        ],
        output,
    )
    with open("test_files/filter_output.csv", newline="") as output_file:
        expected_output = output_file.read()
    assert output.getvalue() == expected_output
