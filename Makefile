# todo:

default: 00 01 02 02b

00:
	python examples/00deps.py

01:
	python examples/01dot.py

02:
	modulegraph examples/02dump_json.py

02b:
	modulegraph "examples/02dump_json.py:main" --name=bar
