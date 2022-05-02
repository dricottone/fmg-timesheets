#!/usr/bin/env python3

import sys
import pathlib

from parser.xml import parse as parse_xml
from parser.pdf import parse as parse_pdf
from parser.timesheet import TimeSheet

def main(filelist):
    print(f"processing {len(filelist)} files")
    for filename in (filelist):
        xml_filename = filename.parent.joinpath(filename.name + ".xml")
        csv_filename = filename.parent.joinpath(filename.name + ".csv")

        parse_pdf(filename, xml_filename)
        parse_xml(xml_filename, csv_filename)

        #timesheet = TimeSheet(semistructured_data)
        #timesheet.report_issues()

if __name__ == "__main__":
    filelist = []
    for filename in sys.argv[1:]:
        filepath = pathlib.Path(filename)
        if filepath.exists():
            filelist.append(filepath)
        else:
            print(f"no such file: '{filename}'")
    main(filelist)

