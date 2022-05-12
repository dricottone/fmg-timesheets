#!/usr/bin/env python3

def totals(timesheets):
    projects = {}

    for timesheet in timesheets:
        for entry in timesheet:
            key = entry.project
            if entry.time_code in ("HOL", "OTU", "VAC", "OPL", ):
                key = entry.time_code

            if key not in projects.keys():
                projects[key] = {}
                projects[key]["name"] = entry.label
                projects[key]["hours"] = 0

            for hours in entry.data.values():
                projects[key]["hours"] += hours

    for project, data in projects.items():
        print(f"{project:20} {data['name']:100} {data['hours']}")

def total_ocps2020(timesheets):
    total = 0
    for timesheet in timesheets:
        for entry in timesheet:
            if entry.project == "20032.001.20.005":
                for date, hours in entry.data.items():
                    total += hours
                break
    print(f"{total} hours spent on OCPS 2020")

