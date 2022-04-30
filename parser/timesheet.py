#!/usr/bin/env python3

from re import compile as re_compile

PATTERNS = (
    re_compile("[ADFJMNOS][aceopu][bcglnprtvy] [1-9][0-9]?, 20[12][89012] [012][0-9]:[0-5][0-9]"),
    re_compile("\(GMT-0[456]:00\) .*"),
    re_compile("Page [1-9][0-9]?"),
    re_compile("of [1-9][0-9]?"),
    re_compile("Timesheet"),
    re_compile("[ADFJMNOS][aceopu][bcglnprtvy] [1-9][0-9]?, 20[12][89012] - [ADFJMNOS][aceopu][bcglnprtvy] [1-9][0-9]?, 20[12][89012]"),
    re_compile("ID"),
    re_compile("Time Code"),
    re_compile("Project"),
    re_compile("TimeType"),
)

def move_item(data, index, destination):
    """Re-order a list, moving an item from `index` to `destination`."""
    if index < destination:
        return data[:index] + data[index+1:destination+1] + data[index:index+1] + data[destination+1:]
    elif index > destination:
        return data[:destination] + data[index:index+1] + data[destination:index] + data[index+1:]
    else:
        return data

def remove_item(data, index):
    """Adjust a list, removing an item from `index`."""
    del data[index]
    return data

def is_multiple_8(string):
    try:
        return int(float(string)) % 8 == 0
    except:
        return False

class Timesheet(object):
    def __init__(self, semistructured_data):
        self._issues = []
        self._data = self.beat_data_with_a_stick(semistructured_data)
        self.assert_header()
        self.parse_header()
        self.parse_footer()
        self.parse_pages()

    def __str__(self):
        return self.header.get("dates", "Timesheet(...)")

    def report_issues(self):
        if self._issues:
            print(f"There are some issues in the timesheet for {self}...")
            for issue in self._issues:
                print(issue)
            for index, line in enumerate(self._data):
                print(index, line)

    def log_issue(self, *parts):
        self._issues.append(''.join(parts))

    def beat_data_with_a_stick(self, data):
        """A fragile solution to the problems resulting from
        PDF-to-HTML-to-long data conversions.
        """
        # a small number of timesheets have a 'Doc.No.' field
        if data[14][0] == "Doc.No." and data[17][0] == "1":
            self.log_issue("beat_data_with_a_stick: killing 'Doc.No.' fields")
            #Note: subtract 1 due to the other operation realigning indices
            data = remove_item(data, 14)
            data = remove_item(data, 17-1)
        elif data[16][0] == "Doc.No." and data[19][0] == "1":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "killing 'Doc.No.' label and field",
            )
            data = remove_item(data, 16)
            data = remove_item(data, 19-1)

        # 'Post Status:' can float up if the status is 'Not posted'
        if data[6][0] == "Post Status:" and data[7][0] == "Not posted":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "re-sorting post status label and field",
            )
            #Note: add/subtract 1 due to the other operation realigning indices
            data = move_item(data, 6, 17+1)
            data = move_item(data, 7-1, 20)

        # 'Function:' and '[1] Full Time' can float up together
        if data[4][0] == "Function:" and data[5][0] == "[1] Full Time":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "re-sorting function label and field",
            )
            #Note: add/subtract 1 due to the other operation realigning indices
            data = move_item(data, 4, 10+1)
            data = move_item(data, 5-1, 13)
        elif data[8][0] == "Function:" and data[11][0] == "[1] Full Time":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "re-sorting function label and field",
            )
            data = move_item(data, 8, 10)
            data = move_item(data, 11, 13)

        # 'Percent Billability:' can float down
        if data[28][0] == "Percent Billability:":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "re-sorting percent billability label",
            )
            data = move_item(data, 28, 25)

        # 'Validation:' and 'Passed' can float up
        if data[16][0] == "Validation:" and data[19][0] == "Passed":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "re-sorting validation label and field",
            )
            data = move_item(data, 16, 17)
            data = move_item(data, 19, 20)

        # 'Posted'/'Not posted' can float up
        if data[17][0] == "Posted" or data[17][0] == "Not posted":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "re-sorting post status field",
            )
            data = move_item(data, 17, 19)

        # 'ID', 'Time Code', 'Project', and 'TimeType' and float down
        if data[41][0] == "ID" and data[42][0] == "Time Code" and data[43][0] == "Project" and data[44][0] == "TimeType":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "re-sorting ID, Time Code, Project, and TimeType header",
            )
            data = move_item(data, 41, 30)
            data = move_item(data, 42, 31)
            data = move_item(data, 43, 32)
            data = move_item(data, 44, 33)
        elif data[43][0] == "ID" and data[44][0] == "Time Code" and data[45][0] == "Project" and data[46][0] == "TimeType":
            self.log_issue(
                "beat_data_with_a_stick: ",
                "re-sorting ID, Time Code, Project, and TimeType header",
            )
            data = move_item(data, 43, 30)
            data = move_item(data, 44, 31)
            data = move_item(data, 45, 32)
            data = move_item(data, 46, 33)

        return data

    def assert_header_item(self, index, should_be):
        if self._data[index][0] != should_be:
            self.log_issue(
                "assert_header: ",
                f"item {index} is not {should_be} ",
                f"(is {self._data[index][0]})",
            )

    def assert_header_item_any(self, index, should_be_any):
        if self._data[index][0] not in should_be_any:
            self.log_issue(
                "assert_header: ",
                f"item {index} is not one of {', '.join(should_be_any)} ",
                f"(is {self._data[index][0]})",
            )

    def assert_header(self):
        """Validate a document based on the header lines."""
        self.assert_header_item(0, "Timesheet")
        self.assert_header_item(2, "Location:")
        self.assert_header_item(3, "[E01] Fors Marsh Group")
        self.assert_header_item(4, "Department:")
        self.assert_header_item_any(5, ("[3200] Advanced Analytics", "[3230] Data Management", ))
        self.assert_header_item(6, "Employee Type:")
        self.assert_header_item(7, "[1] Annual Salary")
        self.assert_header_item(8, "Location (Default")
        self.assert_header_item(9, "[LOCAL] Location")
        self.assert_header_item(10, "Function:")
        self.assert_header_item(11, "Exempt:")
        self.assert_header_item(12, "Status:")
        self.assert_header_item(13, "[1] Full Time")
        self.assert_header_item(14, "Yes")
        self.assert_header_item_any(15, ("Approved", "Closed", "On Hold [Draft]", ))
        self.assert_header_item(16, "Post Status:")
        self.assert_header_item(17, "Validation:")
        self.assert_header_item(18, "Date/Time:")
        self.assert_header_item_any(19, ("Posted", "Not posted", ))
        self.assert_header_item_any(20, ("Passed", "Warnings", ))
        #21 should be like "Mon N, YYYY HH:MM"
        self.assert_header_item(22, "Total Timesheet:")
        self.assert_header_item(23, "Standard Hours:")
        self.assert_header_item(24, "Total Billable:")
        self.assert_header_item(25, "Percent Billability:")
        if not is_multiple_8(self._data[27][0]):
            self.log_issue(
                "assert_header: ",
                "item 27 is not a multiple of 8 ",
                f"(is {self._data[27]})",
            )
        self.assert_header_item(30, "ID")
        self.assert_header_item(31, "Time Code")
        self.assert_header_item(32, "Project")
        self.assert_header_item(33, "TimeType")

    def parse_header(self):
        """Read data from the document header and clear those lines."""
        self.header = {
            "dates": self._data[1][0],
            "employ_location": self._data[3][0],
            "employ_location_default": self._data[9][0],
            "employ_dept": self._data[5][0],
            "employ_type": self._data[7][0],
            "employ_exempt": self._data[14][0],
            "status": self._data[15][0],
            "status_posting": self._data[19][0],
            "status_validation": self._data[20][0],
            "status_timestamp": self._data[21][0],
            "hours": self._data[26][0],
            "hours_minimum": self._data[27][0],
            "hours_billable": self._data[28][0],
            "percent_billable": self._data[29][0],
        }
        del self._data[:34]

    def parse_footer(self):
        """Loop though lines to identify the document footer and clear it."""
        target = None
        for n in range(len(self._data)-1, 0, -1):
            if self._data[n][0] == "Hours Distribution by Time Code":
                target = n
                break
        if target is None:
            self.log_issue(
                "parse_footer: ",
                "could not locate document footer",
            )
        else:
            del self._data[target:]

    def parse_pages(self):
        """Loop through lines to identify page headers and footers, and clear
        those lines.
        """
        page_breaks = []
        for index, line in enumerate(self._data):
            if line[0] == "Timesheet":
                page_breaks.append(index)
        if not page_breaks:
            self.log_issue(
                "parse_pages: ",
                "could not locate any page breaks",
            )

        for page_break in reversed(page_breaks):
            i = page_break - 7
            while i < page_break:
                j = 0
                while j < len(PATTERNS):
                    if PATTERNS[j].match(self._data[i][0]):
                        del self._data[i]
                        j = 0
                    else:
                        j += 1
                i += 1

