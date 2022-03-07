# pwk

[![Test](https://github.com/saeub/pwk/actions/workflows/test.yaml/badge.svg)](https://github.com/saeub/pwk/actions/workflows/test.yaml)
[![Publish](https://github.com/saeub/pwk/actions/workflows/publish.yaml/badge.svg)](https://github.com/saeub/pwk/actions/workflows/publish.yaml)
[![PyPI](https://img.shields.io/pypi/v/pwk?label=PyPI)](https://pypi.org/project/pwk/)

**pwk** is a simple script to quickly process and reformat tabular data using Python expressions.

Inspired by [AWK](https://en.wikipedia.org/wiki/AWK).

## Requirements

- Python >= 3.6

## Installing

Download [`pwk.py`](https://github.com/saeub/pwk/blob/main/pwk.py) and put it somewhere in your `PATH`.

You can use this command to download and install the script directly into `/usr/local/bin`:

```sh
curl 'https://raw.githubusercontent.com/saeub/pwk/main/pwk.py' > /usr/local/bin/pwk && chmod +x /usr/local/bin/pwk
```

## Examples

```sh
$ cat prices_without_tax.csv
car,20000
bike,600
motorcycle,3000

$ pwk '_1.title(), _2*1.07' prices_without_tax.csv
Car     21400.0
Bike    642.0
Motorcycle      3210.0
```

```sh
$ cat shopping_list.csv
bread and butter,2.50,supermarket
"apples, pears and oranges",4.20,fruit store
chocolate,1.10,supermarket

$ pwk -s -i csv -o tsv '"$"+_2, _1' shopping_list.csv
$2.50   bread and butter
$4.20   apples, pears and oranges
$1.10   chocolate
```

## Running tests

- Install development dependencies: `pip install -r dev-requirements.txt`
- Run tests: `pytest test.py`

## Similar projects

- [github.com/alecthomas/pawk](https://github.com/alecthomas/pawk)
- [github.com/jasontrigg0/pawk](https://github.com/jasontrigg0/pawk)

The main advantage of this project is saving an "a" in the command.
