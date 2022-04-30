#!/usr/bin/env python3

import sys
import pathlib

import parse

def main(filelist):
    print(f"processing {len(filelist)} files")
    for filename in (filelist):
        parse.timesheet(filename)

if __name__ == "__main__":
    filelist = []
    for filename in sys.argv[1:]:
        filepath = pathlib.Path(filename)
        if filepath.exists():
            filelist.append(filepath)
        else:
            print(f"no such file: '{filename}'")
    main(filelist)

