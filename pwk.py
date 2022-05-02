#! /usr/bin/env python3

import argparse
import csv
import importlib
import itertools
import math
import re
import sys
import unicodedata
from types import CodeType, ModuleType
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    Match,
    Optional,
    Sequence,
    TextIO,
    Tuple,
)

INCLUDE_GLOBALS = {
    # math
    **{key: value for key, value in math.__dict__.items() if not key.startswith("_")},
    # re
    "findall": re.findall,
    "fullmatch": re.fullmatch,
    "match": re.match,
    "search": re.search,
    "split": re.split,
    "sub": re.sub,
    "subn": re.subn,
    # unicodedata
    "normalize": unicodedata.normalize,
    # builtins
    "abs": abs,
    "all": all,
    "any": any,
    "ascii": ascii,
    "bin": bin,
    "bool": bool,
    "bytearray": bytearray,
    "bytes": bytes,
    "chr": chr,
    "complex": complex,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "format": format,
    "frozenset": frozenset,
    "hash": hash,
    "hex": hex,
    "id": id,
    "int": int,
    "iter": iter,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "next": next,
    "object": object,
    "oct": oct,
    "ord": ord,
    "pow": pow,
    "range": range,
    "repr": repr,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,
}


def get_outputs(obj: Any, recurse: bool = True) -> Tuple[str, ...]:
    if isinstance(obj, str):
        return (obj,)
    if isinstance(obj, Match):
        if len(obj.groups()) > 0:
            return tuple(obj.groups())
        return (obj.group(0),)
    if isinstance(obj, Iterable) and recurse:
        return tuple(
            output for field in obj for output in get_outputs(field, recurse=False)
        )
    return (str(obj),)


def evaluate(
    expr: CodeType,
    field_values: Dict[int, Any],
    field_names: Optional[Sequence[str]] = None,
    row_number: Optional[int] = None,
    imported_modules: Optional[Dict[str, ModuleType]] = None,
):
    namespace: Dict[str, Any] = INCLUDE_GLOBALS
    if imported_modules is not None:
        namespace.update(imported_modules)
    namespace.update({f"_{i}": field for i, field in field_values.items()})
    if field_names is not None:
        namespace["_"] = {
            name: field_values[i + 1] for i, name in enumerate(field_names)
        }
    if row_number is not None:
        namespace["_n"] = row_number
    namespace["__builtins__"] = {}

    result = eval(expr, namespace)
    if result is None:
        return None
    return get_outputs(result)


def process(
    expr: CodeType,
    rows: Iterable[Sequence[Any]],
    field_names: Optional[Sequence[str]],
    imported_modules: Dict[str, ModuleType],
):
    for row_number, fields in enumerate(rows):
        result = evaluate(
            expr,
            {i: field for i, field in enumerate((fields,) + tuple(fields))},
            field_names=field_names,
            row_number=row_number,
            imported_modules=imported_modules,
        )
        yield result


def process_aggregate(
    expr: CodeType,
    rows: Iterable[Sequence[Any]],
    field_names: Optional[Sequence[str]],
    imported_modules: Dict[str, ModuleType],
):
    if field_names is not None:
        num_fields = len(field_names)
    else:
        highest_mentioned_field_number = 0
        for name in expr.co_names:
            match = re.match(r"^_(\d+)$", name)
            if match is not None:
                field_number = int(match.group(1))
                if field_number > highest_mentioned_field_number:
                    highest_mentioned_field_number = field_number
        num_fields = highest_mentioned_field_number

    field_values = {}
    row_iterators = itertools.tee(rows, num_fields)
    for field_number, row_iterator in enumerate(row_iterators):
        field_values[field_number + 1] = [
            fields[field_number] for fields in row_iterator
        ]

    result = evaluate(
        expr, field_values, field_names=field_names, imported_modules=imported_modules
    )
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
    parser = argparse.ArgumentParser()

    def compile_expr(expr):
        return compile(expr, "pwk_expr", "eval")

    parser.add_argument("expr", type=compile_expr)
    parser.add_argument("file", type=open, nargs="?", default=sys.stdin)

    parser.add_argument(
        "-i", dest="input_format", choices=["csv", "tsv", "ssv", "plain"]
    )
    parser.add_argument(
        "-o", dest="output_format", choices=["csv", "tsv", "ssv", "plain"]
    )

    parser.add_argument("-s", dest="string_numbers", action="store_true")
    parser.add_argument("-a", dest="aggregate", action="store_true")
    parser.add_argument("-H", dest="header", action="store_true")
    parser.add_argument("-I", dest="imports")

    args = parser.parse_args(cmdargs)
    args.imports = args.imports.split(",") if args.imports else []

    if args.input_format is None:
        if args.file.name.endswith(".csv"):
            args.input_format = "csv"
        elif args.file.name.endswith(".tsv"):
            args.input_format = "tsv"
        elif args.file.name.endswith(".ssv"):
            args.input_format = "ssv"
        else:
            args.input_format = "plain"
    if args.output_format is None:
        args.output_format = "plain"

    return args


def main(cmdargs: Optional[Sequence[str]] = None, output_file: TextIO = sys.stdout):
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
    elif args.input_format == "ssv":
        reader = csv.reader(args.file, delimiter=";")
    elif args.input_format == "plain":
        reader = ((row.rstrip("\n\r"),) for row in args.file)

    if args.output_format == "csv":
        writer = csv.writer(output_file, delimiter=",").writerow
    elif args.output_format == "tsv":
        writer = csv.writer(output_file, delimiter="\t").writerow
    elif args.output_format == "ssv":
        writer = csv.writer(output_file, delimiter=";").writerow
    elif args.output_format == "plain":

        def writer(fields):
            output_file.write("\t".join(fields))
            output_file.write("\n")

    field_names = None
    if args.header:
        field_names = next(reader)

    imported_modules = {
        module_name: importlib.import_module(module_name)
        for module_name in args.imports
    }

    rows = ([preprocess(field) for field in fields] for fields in reader)

    if args.aggregate:
        processor = process_aggregate(args.expr, rows, field_names, imported_modules)
    else:
        processor = process(args.expr, rows, field_names, imported_modules)

    for fields in processor:
        if fields is not None:
            writer([postprocess(field) for field in fields])


if __name__ == "__main__":
    main()
