#!/usr/bin/env python3

"""The parsers are developed, debugged, and refactored in this file.

When they mature, I refactor them into standalone modules under the `parser`
directory.

Eventually, the entire parse step will mature and be abstracted into a
single function call, which will be appropriate to call in `main.py`.

If you can see this file, then I'm not done yet.
"""

from pprint import pprint

from parser.html import parse as parse_html
from parser.pdf import parse as parse_pdf

def read_timesheet(filename):
    unstructured_data = parse_pdf(filename)
    semistructured_data = parse_html(unstructured_data)
    return semistructured_data

def has_style_left(attrs):
    return "style" in attrs.keys() and "left" in attrs["style"].keys()

def update_count(counters, key):
    if key in counters.keys():
        counters[key] += 1
    else:
        counters[key] = 1
    return counters

def parse_timesheet(data):

    in_div = False
    in_span = False
    left = ""

    for line in data:
        if in_span:
            if line[0] == "DATA":
                print(f"{left:10} {line[2][0]}")
            in_span = False
            in_div = False
        elif in_div:
            if line[0] == "START" and line[1] == "span":
                in_span = True
            else:
                in_div = False
        else:
            if line[0] == "START" and line[1] == "div" and has_style_left(line[2]):
                in_div = True
                left = line[2]["style"]["left"]

    return []

def extract_projects(structured_data):
    return []

def timesheet(filename):
    unstructured_data = read_timesheet(filename)
    structured_data = parse_timesheet(unstructured_data)
    projects = extract_projects(structured_data)
    return projects

