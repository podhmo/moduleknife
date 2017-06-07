moduleknife
========================================

.. code-block:: console

  $ moduelgraph 02dump_json.py
  {
     "age": 20,
     "name": "foo"
  }
  digraph g {
      g0 [label="json"]
      g1 [label="json.encoder"]
      g2 [label="json.decoder"]
      g3 [label="argparse"]
      g4 [label="copy"]
      g5 [label="gettext"]
      g6 [label="textwrap"]
      g7 [label="json.scanner"]
      g8 [label="02dump_json"]
      g9 [label="locale"]
      g10 [label="struct"]
      g0 -> g1
      g0 -> g2
      g3 -> g4
      g3 -> g5
      g3 -> g6
      g2 -> g7
      g8 -> g0
      g8 -> g3
      g5 -> g9
      g5 -> g10
  }
  $ moduelgraph 02dump_json.py --outfile=02dump_json.dot
  {
    "age": 20,
    "name": "foo"
  }
  write 02dump_json.dot...
  $ moduelgraph 02dump_json.py --driver=ToplevelOnlyDriver --outfile=02dump_json2.dot
  {
    "age": 20,
    "name": "foo"
  }
  write 02dump_json2.dot...


02dump_json.py

.. code-block:: python

  import json
  import sys
  import argparse


  def main():
      parser = argparse.ArgumentParser()
      parser.add_argument("--name", default="foo")

      args = parser.parse_args()

      person = {"name": args.name, "age": 20}
      json.dump(person, sys.stdout, indent=2)


  if __name__ == "__main__":
      main()
  else:
      print("hmm")


`02dump_json.svg <./misc/readme.svg>`_
`02dump_json2.svg <./misc/readme2.svg>`_
