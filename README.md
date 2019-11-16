# pwk

A *very* simple application to quickly process and reformat tabular data using Python expressions.

Inspired by AWK.

## Installing

- clone this repo
- put a link to `pwk.py` somewhere in your PATH

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


$ cat shopping_list.csv
bread and butter,2.50,supermarket
"apples, pears and oranges",4.20,fruit store
chocolate,1.10,supermarket

$ pwk -s -i csv -o tsv '"$"+_2, _1' shopping_list.csv
$2.50   bread and butter
$4.20   apples, pears and oranges
$1.10   chocolate
```

## Similar projects

- [github.com/alecthomas/pawk](https://github.com/alecthomas/pawk)
- [github.com/jasontrigg0/pawk](https://github.com/jasontrigg0/pawk)

The main advantage of this project is saving an "a" in the command.
