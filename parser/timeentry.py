#!/usr/bin/env python3

from re import compile as re_compile

PROJECT_PATTERN = re_compile("(OHORG\.(MTG|ONB|PFR|TPD|TOH)\.[01][0-9]\.00[0-9]|UNALW\.EMW\.0[0-9]\.00[0-9]|FSERV\.PPM\.00\.000|[0-9]{5}\.[0-9]{3}\.[0-9]{2}\.[0-9]{3})")
TIMETYPE_PATTERN = re_compile("(FSERV|[0-9]{3,5})")
DATE_PATTERN = re_compile("[ADFJMNOS][aceopu][bcglnprtvy] [0-9][0-9]?, 20[12][89012]")

ENTRY_PATTERNS = (
    re_compile("[1-9][0-9]?"),
    re_compile("(HOL|OTU|ST|VAC)"),
    re_compile("(OHORG\.(MTG|ONB|PFR|TPD|TOH)\.[01][0-9]\.00[0-9]|UNALW\.EMW\.0[0-9]\.00[0-9]|FSERV\.PPM\.00\.000|[0-9]{5}\.[0-9]{3}\.[0-9]{2}\.[0-9]{3})"),
    re_compile("(FSERV|[0-9]{3,5})"),
    re_compile("."),
    re_compile("Notes"),
    re_compile("[ADFJMNOS][aceopu][bcglnprtvy] [0-9][0-9]?, 20[12][89012] -"),
    re_compile("[ADFJMNOS][aceopu][bcglnprtvy] [0-9][0-9]?, 20[12][89012] Other"),
    re_compile("."),
    re_compile("Approved"),
)

class TimeEntry(object):
    def __init__(self, semistructured_data, timesheet_name, entry_number):
        self._issues = []
        self._timesheet = timesheet_name
        self._entry = entry_number
        self._data = self.beat_data_with_a_stick(semistructured_data)
        self.parse_entry_number()
        self.parse_entry_project()
        self.parse_entry_notes()
        self.parse_entry_approval()

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


    def assert_entry_item_any(self, index, label, should_be_any):
        if self._data[index][0] not in should_be_any:
            self.log_issue(
                "parse_entry: ",
                f"{label} not one of {', '.join(should_be_any)} ",
                f"(is {self._data[index][0]})",
            )

    def assert_entry_item_match(self, index, label, pattern):
        if not pattern.match(self._data[index][0]):
            self.log_issue(
                "parse_entry: ",
                f"{label} does not look correct ",
                f"(is {self._data[index][0]})",
            )

    def assert_entry_item_at(self, index, label, should_be_at):
        if self._data[index][1] != should_be_at:
            self.log_issue(
                "parse_entry: ",
                f"{label} not at {should_be_at}px left ",
                f"(is at {self._data[index][1]}px)",
            )

    def parse_entry_number(self):
        del self._data[0]

    def parse_entry_project(self):
        self.assert_entry_item_any(0, "time code", ("HOL", "OTU", "ST", "VAC", ))
        self.assert_entry_item_at(0, "time code", 40)
        self._timecode = self._data[0][0]
        del self._data[0]

        if self._timecode in ("HOL", "OTU", "VAC", ):
            self._project = ""
            self._timetype = ""
        elif " " in self._data[0][0]:
            self.assert_entry_item_match(0, "project", PROJECT_PATTERN)
            self.assert_entry_item_at(0, "project", 120)
            project_timetype = self._data[0][0].split(" ", 1)
            self._project = project_timetype[0]
            self._timetype = project_timetype[1]
            del self._data[0]
        else:
            self.assert_entry_item_match(0, "project", PROJECT_PATTERN)
            self.assert_entry_item_at(0, "project", 120)
            self._project = self._data[0][0]
            self.assert_entry_item_match(1, "time type", TIMETYPE_PATTERN)
            self.assert_entry_item_at(1, "time type", 201)
            self._timetype = self._data[0][0]
            del self._data[0:2]

        self._name = self._data[0][0]
        del self._data[0]

    def parse_entry_note(self):
        if self._data[0][0] == "Line Note:":
            # There is no start or end field, just the text field
            self._notes.append({
                "start": "",
                "end": "",
                "text": self._data[1][0],
            })
            del self._data[0:2]
        else:
            match = DATE_PATTERN.match(self._data[0][0])
            if match:
                self._notes.append({})

                # Handle the start field
                self.assert_entry_item_at(0, "note start", 40)
                self._notes[-1]["start"] = match

                # Handle the start/end separator if it is separate from the
                # start field
                if self._data[1][0] == "-":
                    del self._data[1]

                # Handle the end field
                self.assert_entry_item_at(1, "note end", 99)
                match = DATE_PATTERN.match(self._data[1][0])
                if match:
                    self._notes[-1]["end"] = match

                # Handle the 'Approved' note if it floated up
                if self._data[2][0] == "Approved":
                    del self._data[2]

                # Handle the text field
                self.assert_entry_item_at(2, "note text", 201)
                self._notes[-1]["text"] = self._data[2][0]

                del self._data[0:3]

    def parse_entry_notes(self):
        print(self._data)
        self._notes = []
        if len(self) and self._data[0][0] == "Notes":
            del self._data[0]

            # One or two notes follow
            if len(self):
                self.parse_entry_note()
            if len(self):
                self.parse_entry_note()

    def parse_entry_approval(self):
        if len(self) and self._data[0][0] == "Approved":
            del self._data[0]

    def beat_data_with_a_stick(self, data):
        data = [i for i in data if i[1]<400] + [i for i in data if i[1]>=400]
        return data

