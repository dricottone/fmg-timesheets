#!/usr/bin/env python3

import sys
import pathlib
from pprint import pprint

from parser.xml import parse as parse_xml
from parser.pdf import parse as parse_pdf
from parser.timesheet import parse as parse_timesheet

def main(filelist):
    projects = {}

    print(f"processing {len(filelist)} files")
    for filename in (filelist):
        xml_filename = filename.parent.joinpath(filename.name + ".xml")
        csv_filename = filename.parent.joinpath(filename.name + ".csv")

        parse_pdf(filename, xml_filename)
        parse_xml(xml_filename, csv_filename)

        entries = parse_timesheet(csv_filename)
        for entry in entries:
            if entry.time_code in ("HOL", "OTU", "VAC", "OPL", ):
                if entry.time_code not in projects.keys():
                    projects[entry.time_code] = {}
                for date, hours in entry.data.items():
                    projects[entry.time_code][date] = hours
            else:
                if entry.project not in projects.keys():
                    projects[entry.project] = {}
                for date, hours in entry.data.items():
                    projects[entry.project][date] = hours

    pprint(projects)

if __name__ == "__main__":
    filelist = []
    for filename in sys.argv[1:]:
        filepath = pathlib.Path(filename)
        if filepath.exists():
            filelist.append(filepath)
        else:
            print(f"no such file: '{filename}'")
    main(filelist)

