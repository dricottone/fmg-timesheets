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
from parser.timesheet import TimeSheet

def read_timesheet(filename):
    unstructured_data = parse_pdf(filename)
    semistructured_data = parse_html(unstructured_data)
    return semistructured_data

def parse_timesheet(data):
    t = TimeSheet(data)
    t.report_issues()
    return []

def extract_projects(structured_data):
    return []

def timesheet(filename):
    semistructured_data = read_timesheet(filename)
    structured_data = parse_timesheet(semistructured_data)
    projects = extract_projects(structured_data)
    return projects

