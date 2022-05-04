#!/usr/bin/env python3

import csv

def handle_date(date):
    return date.strftime("%m/%d/%Y")

def encode_list(timesheets):
    """Given a list of timesheets, which themselves are lists of time entries,
    create a long list of data.

    ```
    [ ['PROJECT', 'MM/DD/YYYY', decimal.Decimal(HOURS)],
      ...
    ]
    ```
    """
    projects = []

    for timesheet in timesheets:
        for entry in timesheet:
            # identify the project key to use
            key = entry.project
            if entry.time_code in ("HOL", "OTU", "VAC", "OPL", ):
                key = entry.time_code

            # set hours into the projects list
            for date, hours in entry.data.items():
                projects.append([key, handle_date(date), hours])

    return projects

def export(filename, timesheets):
    """Main routine."""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        for row in encode_list(timesheets):
            writer.writerow(row)

