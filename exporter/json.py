#!/usr/bin/env python3

#TODO: dumps dictionary into JSON file

def encode_dict(timesheets):
    """Given a list of timesheets, which themselves are lists of time entries,
    create a nested dictionary to represent the data.

    ```
    {
      'PROJECT': {
        datetime.datetime(DATE): decimal.Decimal(HOURS),
        ...
      },
      ...
    }
    ```
    """
    projects = {}

    for timesheet in timesheets:
        for entry in timesheet:
            # identify the project key to use
            key = entry.project
            if entry.time_code in ("HOL", "OTU", "VAC", "OPL", ):
                key = entry.time_code

            # set new dictionary for new keys
            if key not in projects.keys():
                projects[key] = {}

            # set hours into the projects dictionary
            for date, hours in entry.data.items():
                projects[key][date] = hours

    return projects

def export(filename, timesheets):
    pass

