#!/usr/bin/env python3

from re import compile as re_compile

ENTRY_PATTERNS = (
    re_compile("[1-9][0-9]?"),
    re_compile("(ST|VAC|HOL)"),
    re_compile("(OHORG\.(MTG|ONB)\.0[0-5]\.00[0-5]|UNALW\.EMW\.0[0-5]\.00[0-5]|[0-9]{5}\.[0-9]{3}\.[0-9]{2}\.[0-9]{3})"),
    re_compile("[0-9]{3,5}"),
    re_compile("."),
    re_compile("Notes"),
    re_compile("[ADFJMNOS][aceopu][bcglnprtvy] [1-9][0-9]?, 20[12][89012]"),
    re_compile("- [ADFJMNOS][aceopu][bcglnprtvy] [1-9][0-9]?, 20[12][89012]"),
    re_compile("."),
)

class TimeEntry(object):
    def __init__(self, semistructured_data, timesheet_name, entry_number):
        self._issues = []
        self._timesheet = timesheet_name
        self._entry = entry_number
        self._data = self.beat_data_with_a_stick(semistructured_data)
        self.assert_entry()

    def __str__(self):
        return f"entry #{self._entry} in the timesheet for {self._timesheet}"

    def __len__(self):
        return len(self._data)

    def report_issues(self):
        if self._issues:
            print(f"There are some issues in {self}...")
            for issue in self._issues:
                print(issue)
            for index, line in enumerate(self._data):
                print(index, line)

    def log_issue(self, *parts):
        self._issues.append(''.join(parts))

    def beat_data_with_a_stick(self, data):
        # Project and TimeType fields can get merged
        if " " in data[2][0]:
            project_timetype = data[2][0].split(" ", 1)
            shared = [n for n in data[2][1:]]
            split = [
                (project_timetype[0], *shared, ),
                (project_timetype[1], *shared, ),
            ]
            data = data[:2] + split + data[3:]

        # Holiday and Vacation time entries skip the Project and TimeType fields
        if data[1][0] in ("HOL", "VAC", ):
            data = data[0:1] + [("", 0, ), ("", 0, )] + data[1:]

        return data

    def assert_entry_item(self, index, should_be_at):
        if not ENTRY_PATTERNS[index].match(self._data[index][0]):
            self.log_issue(
                "assert_entry: ",
                f"item {index} does not look right ",
                f"({self._data[index][0]})",
            )
        if self._data[index][1] != should_be_at:
            self.log_issue(
                "assert_entry: ",
                f"item {index} is not at {should_be_at}px left ",
                f"(is at {self._data[index][1]}px)",
            )

    def assert_entry(self):
        self.assert_entry_item(1, 40)
        self.assert_entry_item(2, 120)
        self.assert_entry_item(3, 201)
        print(self._data)
        self.assert_entry_item(4, 39)
        if len(self)>5 and self._data[5] == "Notes":
            self.assert_entry_item(5, 40)
            self.assert_entry_item(6, 40)
            self.assert_entry_item(7, 99)
            self.assert_entry_item(8, 220)

