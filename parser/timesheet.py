#!/usr/bin/env python3

import datetime
import decimal
import csv
import sys
from re import compile as re_compile

ID_PATTERN = re_compile("[1-2]?[0-9]$")
TIME_CODE_PATTERN = re_compile("(ST|VAC|HOL|OTU|OPL)")
PROJECT_PATTERN = re_compile("[A-Z0-9]{5}\.[A-Z0-9]{3}\.[A-Z0-9]{2}\.[A-Z0-9]{3}")
TIMETYPE_PATTERN = re_compile("[A-Z0-9.]{3,}")
WEEK_BEGINNING_AND_WEEK_PATTERN = re_compile("Week Beginning: [0-9][0-9] [ADFJMNOS][aceopu][bcglnprtvy], 20[12][89012]")
WEEK_BEGINNING_PATTERN = re_compile("Week Beginning:")
WEEK_PATTERN = re_compile("[0-9][0-9] [ADFJMNOS][aceopu][bcglnprtvy], 20[12][89012]")
HOURS_PATTERN = re_compile("[0-9][0-9]?\.(00|25|50|75)")
TOTAL_HOURS_PATTERN = re_compile("Total Hours for line ")
APPROVED_PATTERN = re_compile("Approved")
NOTES_PATTERN = re_compile("Notes")

def printf(string, *variables):
    """Print to STDERR with formatting."""
    sys.stderr.write(string.format(*variables))
    sys.stderr.write("\n")

def is_approximately(location, target):
    """Tests if a location is close enough to a target to be considered equal.

    PDFs store the rendered location of a textbox, not the mathematically-
    ideal location. The net effect is that, while you can rely on the y
    dimension to identify a row, you cannot rely on the x dimension to
    identify a column. My solution is to make equivalence a bit fuzzy, to the
    effect of +/- 5 pixels.
    """
    return (target-8 <= location <= target+8)

class TimeEntry(object):
    def __init__(self):
        self.label = None
        self.project = None
        self.time_code = None
        self.data = {}
        self.reference_date = None
        self.in_notes = False

    def assert_equal(self, value, should_be):
        if value != should_be:
            printf("{0} is not {1}", value, should_be)

    def set_hours(self, day_offset, hours):
        """Given a string like '1.25' and a day offset between 0 and 6, set
        hours into a date.
        """
        if self.reference_date is None:
            printf(
                "hours ({0}) set before a reference date",
                hours,
            )
            return

        target = self.reference_date
        if day_offset != 0:
            target += datetime.timedelta(days=day_offset)
        self.data[target] = decimal.Decimal(hours)

    def set_total_week_hours(self, total_hours):
        """Given a string like '1.25', validate set hours for a week."""
        if self.reference_date is None:
            printf(
                "total week hours ({0}) set before a reference date",
                total_hours,
            )
            return

        target = self.reference_date
        sum_hours = decimal.Decimal(0)
        for _ in range(7):
            if target in self.data:
                sum_hours += self.data[target]
            target += datetime.timedelta(days=1)

        self.assert_equal(sum_hours, decimal.Decimal(total_hours))

    def set_total_line_hours(self, total_hours):
        """Given a string like '1.25', validate set hours for a line entry."""
        if self.reference_date is None:
            printf(
                "total line hours ({0}) set before a reference date",
                total_hours,
            )
            return

        sum_hours = decimal.Decimal(0)
        for date, hours in self.data.items():
            sum_hours += hours

        self.assert_equal(sum_hours, decimal.Decimal(total_hours))

    def advance_reference_date(self):
        """Mark the reference date as invalid."""
        self.reference_date = None

    def set_reference_date(self, date):
        """Given a string like '01 Jan, 2022', set the reference date for
        subsequent method calls.
        """
        self.reference_date = datetime.datetime.strptime(date, "%d %b, %Y")

    def set_time_code(self, time_code):
        """Given 'ST', 'HOL', or 'VAC', set the time code."""
        self.time_code = time_code

    def set_project(self, project):
        """Given a string like '12345.123.12.123', set the official project
        code.
        """
        self.project = project

    def set_label(self, label):
        """Given a string, set the human-readable project label."""
        if not self.label and not self.in_notes:
            self.label = label

    def mark_notes(self):
        """Mark that an entry is receiving notes. Subsequent labels should be
        ignored.
        """
        self.in_notes = True

class TimeSheet(object):
    def __init__(self, data):
        self.data = data
        self.entries = []
        for row in range(len(self.data)):
            self.parse_row(row)

    def set_hours(self, day, hours):
        """Given a string like '1.25' and a day offset between 0 and 6, set
        hours into a date.
        """
        if " " in hours:
            two_hours = hours.split(" ", 1)
            self.entries[-1].set_hours(day, two_hours[0])
            self.entries[-1].set_hours(day+1, two_hours[1])
        else:
            self.entries[-1].set_hours(day, hours)

    def set_total_week_hours(self, total_hours):
        """Given a string like '1.25', validate set hours for a week."""
        self.entries[-1].set_total_week_hours(total_hours)

    def set_total_line_hours(self, total_hours):
        """Given a string like '1.25', validate set hours for a line entry."""
        self.entries[-1].set_total_line_hours(total_hours)

    def advance_reference_date(self):
        """Mark the reference date as invalid."""
        self.entries[-1].advance_reference_date()

    def set_reference_date(self, date):
        """Given a string like '01 Jan, 2022', set the reference date for
        subsequent method calls.
        """
        self.entries[-1].set_reference_date(date)

    def set_time_code(self, time_code):
        """Given 'ST', 'HOL', or 'VAC', set the time code."""
        self.entries[-1].set_time_code(time_code)

    def set_project(self, project):
        """Given a string like '12345.123.12.123', set the official project
        code.
        """
        self.entries[-1].set_project(project)

    def set_label(self, label):
        """Given a string, set the human-readable project label."""
        self.entries[-1].set_label(label)

    def mark_notes(self):
        """Mark that an entry is receiving notes. Subsequent labels should be
        ignored.
        """
        self.entries[-1].mark_notes()

    def parse_row(self, index):
        """Parse a row of data and dispatch between time entry methods."""
        if len(self.data[index])<3:
            return

        if APPROVED_PATTERN.match(self.data[index][2]):
            pass
        elif WEEK_BEGINNING_AND_WEEK_PATTERN.match(self.data[index][2]):
            self.set_reference_date(self.data[index][2].split(": ", 1)[1])
        elif WEEK_BEGINNING_PATTERN.match(self.data[index][2]):
            self.advance_reference_date()
        elif TOTAL_HOURS_PATTERN.match(self.data[index][2]):
            self.set_total_line_hours(self.data[index][2].split(": ", 1)[1])
        elif WEEK_PATTERN.match(self.data[index][2]):
            self.set_reference_date(self.data[index][2])
        elif HOURS_PATTERN.match(self.data[index][2]):
            x = int(float(self.data[index][0]))
            if is_approximately(x, 572):
                self.set_hours(0, self.data[index][2])
            elif is_approximately(x, 597):
                self.set_hours(1, self.data[index][2])
            elif is_approximately(x, 622):
                self.set_hours(2, self.data[index][2])
            elif is_approximately(x, 647):
                self.set_hours(3, self.data[index][2])
            elif is_approximately(x, 672):
                self.set_hours(4, self.data[index][2])
            elif is_approximately(x, 697):
                self.set_hours(5, self.data[index][2])
            elif is_approximately(x, 722):
                self.set_hours(6, self.data[index][2])
            elif is_approximately(x, 751):
                self.set_total_week_hours(self.data[index][2])
            else:
                printf(
                    "found hours ({0}) but they fell through all conditions",
                    self.data[index][2],
                )
        elif TIME_CODE_PATTERN.match(self.data[index][2]):
            self.set_time_code(self.data[index][2])
        elif PROJECT_PATTERN.match(self.data[index][2]):
            self.set_project(self.data[index][2])
        elif TIMETYPE_PATTERN.match(self.data[index][2]):
            pass
        elif ID_PATTERN.match(self.data[index][2]):
            self.entries.append(TimeEntry())
        elif NOTES_PATTERN.match(self.data[index][2]):
            self.mark_notes()
        else:
            self.set_label(self.data[index][2])

def parse(filename):
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        timesheet = TimeSheet([row for row in reader])
        entries = timesheet.entries
        return entries

