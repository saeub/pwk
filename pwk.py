#! /usr/bin/env python3

import argparse
import csv
import math
import sys


def process(expr, reader, writer, preprocess, postprocess):
    for fields in reader:
        fields = [preprocess(field) for field in fields]
        globals = {f"_{i}": field for i, field in enumerate([fields] + fields)}
        globals["_"] = fields
        globals.update(math.__dict__)
        # TODO: better way to disallow user stupidity?
        globals["input"] = None
        globals["print"] = None

        try:
            result = eval(expr, globals)
            if isinstance(result, (tuple, list)):  # TODO: check if iterable
                result = tuple(postprocess(field) for field in result)
            else:
                result = (postprocess(result),)
        except Exception:
            result = tuple()
        writer(result)


def preprocess_nothing(field):
    return field


def preprocess_numbers(field):
    try:
        return int(field)
    except ValueError:
        try:
            return float(field)
        except ValueError:
            return field


def parse_arguments(cmdargs=None):
    parser = argparse.ArgumentParser()

    def compile_expr(expr):
        compile(expr, "pwk_expr", "eval")

    parser.add_argument("expr", type=compile_expr)
    parser.add_argument("file", type=open, nargs="?", default=sys.stdin)

    parser.add_argument("-i", dest="input_format", choices=["csv", "tsv", "plain"])
    parser.add_argument("-o", dest="output_format", choices=["csv", "tsv", "plain"])

    parser.add_argument("-s", dest="string_numbers", action="store_true")
    parser.add_argument("-a", dest="aggregate", action="store_true")

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


def main(cmdargs, out):
    args = parse_arguments(cmdargs)

    if args.string_numbers:
        preprocess = preprocess_nothing
        postprocess = str
    else:
        preprocess = preprocess_numbers
        postprocess = str

    if args.input_format == "csv":
        reader = csv.reader(args.file, delimiter=",")
    elif args.input_format == "tsv":
        reader = csv.reader(args.file, delimiter="\t")
    elif args.input_format == "plain":
        reader = ((line[:-1],) for line in args.file)

    if args.output_format == "csv":
        writer = csv.writer(out, delimiter=",").writerow
    elif args.output_format == "tsv":
        writer = csv.writer(out, delimiter="\t").writerow
    elif args.output_format == "plain":

        def writer(fields):
            out.write("\t".join(fields))
            out.write("\n")

    process(args.expr, reader, writer, preprocess, postprocess)


if __name__ == "__main__":
    main(None, sys.stdout)
