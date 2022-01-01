#! /usr/bin/env python3

import argparse
import csv
import itertools
import math
import re
import sys
from types import CodeType
from typing import Any, Dict, Iterable, Iterator, Optional, Sequence, TextIO


def evaluate(expr: CodeType, field_values: Dict[int, Any]):
    globals = {f"_{i}": field for i, field in field_values.items()}
    globals.update(math.__dict__)
    # TODO: better way to disallow user stupidity?
    globals["input"] = None
    globals["print"] = None

    try:
        result = eval(expr, globals)
        if isinstance(result, Iterable) and not isinstance(result, str):
            result = tuple(field for field in result)
        else:
            result = (result,)
    except Exception:
        result = tuple()
    return result


def process(expr: CodeType, rows: Iterable[Sequence[Any]]):
    for fields in rows:
        result = evaluate(
            expr, {i: field for i, field in enumerate((fields,) + tuple(fields))}
        )
        yield result


def process_aggregate(expr: CodeType, rows: Iterable[Sequence[Any]]):
    mentioned_fields = set()
    for name in expr.co_names:
        match = re.match(r"^_(\d+)$", name)
        if match is not None:
            field_number = int(match.group(1))
            if field_number > 0:
                mentioned_fields.add(field_number)
    field_values = {}
    row_iterators = itertools.tee(rows, len(mentioned_fields))
    for field_number, row_iterator in zip(mentioned_fields, row_iterators):
        field_values[field_number] = [
            fields[field_number - 1] for fields in row_iterator
        ]

    result = evaluate(expr, field_values)
    yield result


def preprocess_nothing(field: Any):
    return field


def preprocess_numbers(field: Any):
    try:
        return int(field)
    except ValueError:
        try:
            return float(field)
        except ValueError:
            return field


def parse_arguments(cmdargs: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--help", action="help")

    def compile_expr(expr):
        return compile(expr, "pwk_expr", "eval")

    parser.add_argument("expr", type=compile_expr)
    parser.add_argument("file", type=open, nargs="?", default=sys.stdin)

    parser.add_argument("-i", dest="input_format", choices=["csv", "tsv", "plain"])
    parser.add_argument("-o", dest="output_format", choices=["csv", "tsv", "plain"])

    parser.add_argument("-s", dest="string_numbers", action="store_true")
    parser.add_argument("-a", dest="aggregate", action="store_true")
    parser.add_argument("-h", dest="header", action="store_true")

    args = parser.parse_args(cmdargs)

    if args.input_format is None:
        if args.file.name.endswith(".csv"):
            args.input_format = "csv"
        elif args.file.name.endswith(".tsv"):
            args.input_format = "tsv"
        else:
            args.input_format = "plain"
    if args.output_format is None:
        args.output_format = "plain"

    return args


def main(cmdargs: Optional[Sequence[str]], output_file: TextIO):
    args = parse_arguments(cmdargs)

    if args.string_numbers:
        preprocess = preprocess_nothing
        postprocess = str
    else:
        preprocess = preprocess_numbers
        postprocess = str

    reader: Iterator[Sequence[str]]
    if args.input_format == "csv":
        reader = csv.reader(args.file, delimiter=",")
    elif args.input_format == "tsv":
        reader = csv.reader(args.file, delimiter="\t")
    elif args.input_format == "plain":
        reader = ((line[:-1],) for line in args.file)

    if args.output_format == "csv":
        writer = csv.writer(output_file, delimiter=",").writerow
    elif args.output_format == "tsv":
        writer = csv.writer(output_file, delimiter="\t").writerow
    elif args.output_format == "plain":

        def writer(fields):
            output_file.write("\t".join(fields))
            output_file.write("\n")

    if args.header:
        next(reader)

    rows = ([preprocess(field) for field in fields] for fields in reader)

    if args.aggregate:
        processor = process_aggregate(args.expr, rows)
    else:
        processor = process(args.expr, rows)

    for fields in processor:
        writer([postprocess(field) for field in fields])


if __name__ == "__main__":
    main(None, sys.stdout)
