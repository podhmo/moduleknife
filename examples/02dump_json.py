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
