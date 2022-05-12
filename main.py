#!/usr/bin/env python3

import sys
import pathlib
from pprint import pprint

from parser.xml import parse as parse_xml
from parser.pdf import parse as parse_pdf
from parser.timesheet import parse as parse_timesheet

from exporter.long_csv import export

from analysis.totals import totals, total_ocps2020

def main(filelist):
    timesheets = []

    print(f"processing {len(filelist)} files")
    for filename in (filelist):
        xml_filename = filename.parent.joinpath(filename.name + ".xml")
        csv_filename = filename.parent.joinpath(filename.name + ".csv")

        parse_pdf(filename, xml_filename)
        parse_xml(xml_filename, csv_filename)

        timesheets.append(parse_timesheet(csv_filename))

    dest_filename = pathlib.Path("analysis/timesheets_sas.csv")
    export(dest_filename, timesheets)

    total_ocps2020(timesheets)

if __name__ == "__main__":
    filelist = []
    for filename in sys.argv[1:]:
        filepath = pathlib.Path(filename)
        if filepath.exists():
            filelist.append(filepath)
        else:
            print(f"no such file: '{filename}'")
    main(filelist)

