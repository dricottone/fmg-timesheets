#!/usr/bin/env python3

import sys
from xml.sax import handler, make_parser
import csv

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
    if (location[1] == target[1]
        and target[0]-5 <= location[0] <= target[0]+5):
        return True
    return False

class TimeSheetHandler(handler.ContentHandler):
    def __init__(self):
        handler.ContentHandler.__init__(self)

        self.text_buffer = ""
        self.line_buffer = []
        self.page_buffer = []

        self.pagenum = None
        self.daterange = None

        self.in_textbox = False
        self.in_text = False
        self.in_figure = False
        self.in_hours_distribution = False

        self.in_header_footer_parts = {
            "timesheet_label": False,
            "timesheet_value": False,
            "location_label": False,
            "location_value": False,
            "department_label": False,
            "department_value": False,
            "employee_type_label": False,
            "employee_type_value": False,
            "location_default_label": False,
            "location_default_value": False,
            "function_label": False,
            "function_value": False,
            "exempt_label": False,
            "exempt_value": False,
            "status_label": False,
            "status_value": False,
            "post_status_label": False,
            "post_status_value": False,
            "validation_label": False,
            "validation_value": False,
            "datetime_label": False,
            "datetime_value": False,
            "total_timesheet_label": False,
            "total_timesheet_value": False,
            "standard_hours_label": False,
            "standard_hours_value": False,
            "total_billable_label": False,
            "total_billable_value": False,
            "percent_billability_label": False,
            "percent_billability_value": False,
            "id_label": False,
            "time_code_label": False,
            "project_label": False,
            "timetype_label": False,
            "day_label": False,
            "total_label": False,
            "_doc_no_label": False,
            "_doc_no_value": False,
            "footer_datetime_value": False,
            "footer_timezone_value": False,
            "footer_pagenum_value": False,
            "footer_pagecount_value": False,
        }

    def startElement(self, name, attrs):
        if name=="page":
            self.in_figure = False
            self.pagenum = attrs["id"]
        elif name=="figure":
            self.in_figure = True
        elif not self.in_figure and not self.in_hours_distribution:
            if name=="textbox":
                handled = self.handle_header_footer_start(attrs["bbox"])
                if not handled:
                    self.record_location(attrs["bbox"])
                self.in_textbox = True
            elif self.in_textbox and name=="text":
                self.in_text = True

    def characters(self, data):
        if self.in_text:
            self.append_buffer(data)

    def endElement(self, name):
        if name=="page":
            self.sort_lines()
        elif not self.in_figure and not self.in_hours_distribution:
            if name=="textbox":
                handled = self.handle_header_footer_end()
                if not handled:
                    text = self.pop_buffer()
                    if text=="Hours Distribution by Time Code":
                        self.in_hours_distribution = True
                    else:
                        self.record_text(text)
                self.in_textbox = False
            elif name=="text":
                self.in_text = False

    def sort_lines(self):
        """Helper function to perform page-level cleaning on line-level data.
        Manipulates the page buffer and clears the line buffer.
        """
        sorted_lines = sorted(
            self.line_buffer,
            key=lambda x: (-float(x[1]), float(x[0])),
        )
        self.line_buffer = []
        self.page_buffer.append(sorted_lines)

    def record_location(self, data):
        """Helper function to append new location data to the line buffer."""
        self.line_buffer.append(data.split(",")[:2])

    def record_text(self, data):
        """Helper function to append new text data to the line buffer."""
        self.line_buffer[-1].append(data)

    def append_buffer(self, data):
        """Helper function to append new character data to the text buffer."""
        self.text_buffer += data

    def pop_buffer(self):
        """Helper function to grab aggregated character data and reset the
        text buffer.
        """
        data = self.text_buffer
        self.text_buffer = ""
        return data.strip()

    def debug_assert(self, value, should_be, label=""):
        """Helper function to manage validation logic and conditional print
        statements.
        """
        if label:
            printf_label = f"{self.daterange}:{self.pagenum}:{label}:"
        else:
            printf_label = f"{self.daterange}:{self.pagenum}:"

        if isinstance(should_be, tuple):
            if value not in should_be:
                printf(
                    printf_label + "should be {0}, is {1}",
                    "one of " + ", ".join(should_be),
                    value,
                )
        elif value != should_be:
            printf(printf_label + "should be {0}, is {1}", should_be, value)

    def handle_header_footer_start(self, location):
        """Handle header and footer content on a page.

        There is some branching based on whether the current page is the first
        page of a document.

        If a header or footer box is identified (based on its location),
        the parser state is updated so that box's content can be grabbed,
        validated, and suppressed from output upon reaching its end.

        If a box is handled, return True. Otherwise return False to signal
        that further handling is necessary.
        """
        location_xy = location.split(",")[:2]
        identity = ','.join(location_xy)
        loc = (int(float(location_xy[0])), int(float(location_xy[1])), )

        if self.pagenum == "1":
            if is_approximately(loc, (335, 524, )):
                self.in_header_footer_parts["timesheet_label"] = True
                return True

            elif is_approximately(loc, (335, 504, )):
                self.in_header_footer_parts["timesheet_value"] = True
                return True

            elif is_approximately(loc, (20, 481, )):
                self.in_header_footer_parts["location_label"] = True
                return True

            elif is_approximately(loc, (93, 481, )):
                self.in_header_footer_parts["location_value"] = True
                return True

            elif is_approximately(loc, (20, 466, )):
                self.in_header_footer_parts["department_label"] = True
                return True

            elif is_approximately(loc, (93, 466, )):
                self.in_header_footer_parts["department_value"] = True
                return True

            elif is_approximately(loc, (20, 452, )):
                self.in_header_footer_parts["employee_type_label"] = True
                return True

            elif is_approximately(loc, (93, 452, )):
                self.in_header_footer_parts["employee_type_value"] = True
                return True

            elif is_approximately(loc, (20, 437, )):
                self.in_header_footer_parts["location_default_label"] = True
                return True

            elif is_approximately(loc, (93, 437, )):
                self.in_header_footer_parts["location_default_value"] = True
                return True

            elif is_approximately(loc, (230, 481, )):
                self.in_header_footer_parts["function_label"] = True
                return True

            elif is_approximately(loc, (304, 481, )):
                self.in_header_footer_parts["function_value"] = True
                return True

            elif is_approximately(loc, (230, 466, )):
                self.in_header_footer_parts["exempt_label"] = True
                return True

            elif is_approximately(loc, (304, 466, )):
                self.in_header_footer_parts["exempt_value"] = True
                return True

            elif is_approximately(loc, (230, 452, )):
                self.in_header_footer_parts["status_label"] = True
                return True

            elif is_approximately(loc, (304, 452, )):
                self.in_header_footer_parts["status_value"] = True
                return True

            elif is_approximately(loc, (230, 437, )):
                self.in_header_footer_parts["_doc_no_label"] = True
                return True

            elif is_approximately(loc, (304, 437, )):
                self.in_header_footer_parts["_doc_no_value"] = True
                return True

            elif is_approximately(loc, (440, 481, )):
                self.in_header_footer_parts["post_status_label"] = True
                return True

            elif is_approximately(loc, (513, 481, )):
                self.in_header_footer_parts["post_status_value"] = True
                return True

            elif is_approximately(loc, (440, 466, )):
                self.in_header_footer_parts["validation_label"] = True
                return True

            elif is_approximately(loc, (513, 466, )):
                self.in_header_footer_parts["validation_value"] = True
                return True

            elif is_approximately(loc, (440, 452, )):
                self.in_header_footer_parts["datetime_label"] = True
                return True

            elif is_approximately(loc, (513, 452, )):
                self.in_header_footer_parts["datetime_value"] = True
                return True

            elif is_approximately(loc, (651, 481, )):
                self.in_header_footer_parts["total_timesheet_label"] = True
                return True

            elif is_approximately(loc, (751, 481, )):
                self.in_header_footer_parts["total_timesheet_value"] = True
                return True

            elif is_approximately(loc, (651, 466, )):
                self.in_header_footer_parts["standard_hours_label"] = True
                return True

            elif is_approximately(loc, (751, 466, )):
                self.in_header_footer_parts["standard_hours_value"] = True
                return True

            elif is_approximately(loc, (651, 452, )):
                self.in_header_footer_parts["total_billable_label"] = True
                return True

            elif is_approximately(loc, (751, 452, )):
                self.in_header_footer_parts["total_billable_value"] = True
                return True

            elif is_approximately(loc, (651, 437, )):
                self.in_header_footer_parts["percent_billability_label"] = True
                return True

            elif is_approximately(loc, (751, 437, )):
                self.in_header_footer_parts["percent_billability_value"] = True
                return True

            elif is_approximately(loc, (20, 399, )):
                self.in_header_footer_parts["id_label"] = True
                return True

            elif is_approximately(loc, (40, 399, )):
                self.in_header_footer_parts["time_code_label"] = True
                return True

            elif is_approximately(loc, (120, 399, )):
                self.in_header_footer_parts["project_label"] = True
                return True

            elif is_approximately(loc, (200, 399, )):
                self.in_header_footer_parts["timetype_label"] = True
                return True

            elif loc[1]==399 and 370 <= loc[0] <= 730:
                self.in_header_footer_parts["day_label"] = True
                return True

            elif is_approximately(loc, (754, 399, )):
                self.in_header_footer_parts["total_label"] = True
                return True

            elif is_approximately(loc, (20, 27, )):
                self.in_header_footer_parts["footer_datetime_value"] = True
                return True

            elif is_approximately(loc, (120, 27, )):
                self.in_header_footer_parts["footer_timezone_value"] = True
                return True

            elif is_approximately(loc, (688, 27, )):
                self.in_header_footer_parts["footer_pagenum_value"] = True
                return True

            elif is_approximately(loc, (732, 27, )):
                self.in_header_footer_parts["footer_pagecount_value"] = True
                return True

        else:
            if is_approximately(loc, (333, 524, )):
                self.in_header_footer_parts["timesheet_label"] = True
                return True

            elif is_approximately(loc, (333, 504, )):
                self.in_header_footer_parts["timesheet_value"] = True
                return True

            elif is_approximately(loc, (20, 479, )):
                self.in_header_footer_parts["id_label"] = True
                return True

            elif is_approximately(loc, (40, 479, )):
                self.in_header_footer_parts["time_code_label"] = True
                return True

            elif is_approximately(loc, (120, 479, )):
                self.in_header_footer_parts["project_label"] = True
                return True

            elif is_approximately(loc, (200, 479, )):
                self.in_header_footer_parts["timetype_label"] = True
                return True

            elif loc[1]==479 and 370 <= loc[0] <= 730:
                self.in_header_footer_parts["day_label"] = True
                return True

            elif is_approximately(loc, (754, 479, )):
                self.in_header_footer_parts["total_label"] = True
                return True

            elif is_approximately(loc, (20, 27, )):
                self.in_header_footer_parts["footer_datetime_value"] = True
                return True

            elif is_approximately(loc, (120, 27, )):
                self.in_header_footer_parts["footer_timezone_value"] = True
                return True

            elif is_approximately(loc, (688, 27, )):
                self.in_header_footer_parts["footer_pagenum_value"] = True
                return True

            elif is_approximately(loc, (732, 27, )):
                self.in_header_footer_parts["footer_pagecount_value"] = True
                return True

        return False

    def handle_header_footer_end(self):
        """Handle header and footer content on a page.

        If a box is handled, return True. Otherwise return False to signal
        that further handling is necessary.
        """
        if self.in_header_footer_parts["_doc_no_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Doc.No.", label="doc no label")
            self.in_header_footer_parts["_doc_no_label"] = False
            return True

        elif self.in_header_footer_parts["_doc_no_value"]:
            value = self.pop_buffer()
            self.debug_assert(value, "1", label="doc no")
            self.in_header_footer_parts["_doc_no_value"] = False
            return True

        elif self.in_header_footer_parts["timesheet_label"]:
            value = self.pop_buffer()
            self.debug_assert(
                value,
                "Timesheet\n[109015] Ricottone, Dominic",
                label="timesheet label",
            )
            self.in_header_footer_parts["timesheet_label"] = False
            return True

        elif self.in_header_footer_parts["timesheet_value"]:
            self.daterange = self.pop_buffer()
            self.in_header_footer_parts["timesheet_value"] = False
            return True

        elif self.in_header_footer_parts["location_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Location:", label="location label")
            self.in_header_footer_parts["location_label"] = False
            return True

        elif self.in_header_footer_parts["location_value"]:
            value = self.pop_buffer()
            self.debug_assert(value, "[E01] Fors Marsh Group", label="location")
            self.in_header_footer_parts["location_value"] = False
            return True

        elif self.in_header_footer_parts["department_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Department:", label="department label")
            self.in_header_footer_parts["department_label"] = False
            return True

        elif self.in_header_footer_parts["department_value"]:
            value = self.pop_buffer()
            self.debug_assert(
                value,
                ("[3200] Advanced Analytics", "[3230] Data Management", ),
                label="department",
            )
            self.in_header_footer_parts["department_value"] = False
            return True

        elif self.in_header_footer_parts["employee_type_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Employee Type:", label="employee type label")
            self.in_header_footer_parts["employee_type_label"] = False
            return True

        elif self.in_header_footer_parts["employee_type_value"]:
            value = self.pop_buffer()
            self.debug_assert(value, "[1] Annual Salary", label="employee type")
            self.in_header_footer_parts["employee_type_value"] = False
            return True

        elif self.in_header_footer_parts["location_default_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Location (Default", label="location default label")
            self.in_header_footer_parts["location_default_label"] = False
            return True

        elif self.in_header_footer_parts["location_default_value"]:
            value = self.pop_buffer()
            self.debug_assert(value, "[LOCAL] Location", label="location default")
            self.in_header_footer_parts["location_default_value"] = False
            return True

        elif self.in_header_footer_parts["function_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Function:", label="function label")
            self.in_header_footer_parts["function_label"] = False
            return True

        elif self.in_header_footer_parts["function_value"]:
            value = self.pop_buffer()
            self.debug_assert(value, "[1] Full Time", label="function")
            self.in_header_footer_parts["function_value"] = False
            return True

        elif self.in_header_footer_parts["exempt_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Exempt:", label="exempt label")
            self.in_header_footer_parts["exempt_label"] = False
            return True

        elif self.in_header_footer_parts["exempt_value"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Yes", label="exempt")
            self.in_header_footer_parts["exempt_value"] = False
            return True

        elif self.in_header_footer_parts["status_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Status:", label="status label")
            self.in_header_footer_parts["status_label"] = False
            return True

        elif self.in_header_footer_parts["status_value"]:
            value = self.pop_buffer()
            self.debug_assert(
                value,
                ("Approved", "Closed", "On Hold [Draft]", ),
                label="status",
            )
            self.in_header_footer_parts["status_value"] = False
            return True

        elif self.in_header_footer_parts["post_status_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Post Status:", label="post status label")
            self.in_header_footer_parts["post_status_label"] = False
            return True

        elif self.in_header_footer_parts["post_status_value"]:
            value = self.pop_buffer()
            self.debug_assert(
                value,
                ("Posted", "Not posted", ),
                label="post status",
            )
            self.in_header_footer_parts["post_status_value"] = False
            return True

        elif self.in_header_footer_parts["validation_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Validation:", label="validation label")
            self.in_header_footer_parts["validation_label"] = False
            return True

        elif self.in_header_footer_parts["validation_value"]:
            value = self.pop_buffer()
            self.debug_assert(
                value,
                ("Passed", "Warnings", ),
                label="validation",
            )
            self.in_header_footer_parts["validation_value"] = False
            return True

        elif self.in_header_footer_parts["datetime_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Date/Time:", label="datetime label")
            self.in_header_footer_parts["datetime_label"] = False
            return True

        elif self.in_header_footer_parts["datetime_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["datetime_value"] = False
            return True

        elif self.in_header_footer_parts["total_timesheet_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Total Timesheet:", label="total timesheet label")
            self.in_header_footer_parts["total_timesheet_label"] = False
            return True

        elif self.in_header_footer_parts["total_timesheet_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["total_timesheet_value"] = False
            return True

        elif self.in_header_footer_parts["standard_hours_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Standard Hours:", label="standard hours label")
            self.in_header_footer_parts["standard_hours_label"] = False
            return True

        elif self.in_header_footer_parts["standard_hours_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["standard_hours_value"] = False
            return True

        elif self.in_header_footer_parts["total_billable_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Total Billable:", label="total billable label")
            self.in_header_footer_parts["total_billable_label"] = False
            return True

        elif self.in_header_footer_parts["total_billable_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["total_billable_value"] = False
            return True

        elif self.in_header_footer_parts["percent_billability_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Percent Billability:", label="percent billability label")
            self.in_header_footer_parts["percent_billability_label"] = False
            return True

        elif self.in_header_footer_parts["percent_billability_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["percent_billability_value"] = False
            return True

        elif self.in_header_footer_parts["id_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "ID", label="id label")
            self.in_header_footer_parts["id_label"] = False
            return True

        elif self.in_header_footer_parts["time_code_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Time Code", label="time code label")
            self.in_header_footer_parts["time_code_label"] = False
            return True

        elif self.in_header_footer_parts["project_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "Project", label="project label")
            self.in_header_footer_parts["project_label"] = False
            return True

        elif self.in_header_footer_parts["timetype_label"]:
            value = self.pop_buffer()
            self.debug_assert(value, "TimeType", label="timetype label")
            self.in_header_footer_parts["timetype_label"] = False
            return True

        elif self.in_header_footer_parts["day_label"]:
            value = self.pop_buffer()
            self.debug_assert(
                value,
                ("Mon", "Tue Wed", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", ),
                label="day label",
            )
            self.in_header_footer_parts["day_label"] = False
            return True

        elif self.in_header_footer_parts["total_label"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["total_label"] = False
            return True

        elif self.in_header_footer_parts["footer_datetime_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["footer_datetime_value"] = False
            return True

        elif self.in_header_footer_parts["footer_timezone_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["footer_timezone_value"] = False
            return True

        elif self.in_header_footer_parts["footer_pagenum_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["footer_pagenum_value"] = False
            return True

        elif self.in_header_footer_parts["footer_pagecount_value"]:
            value = self.pop_buffer()
            self.in_header_footer_parts["footer_pagecount_value"] = False
            return True

        return False

def parse(filename_in, filename_out):
    """Main routine. Reads an XML file and writes a CSV file."""
    parser = make_parser()
    handler = TimeSheetHandler()

    parser.setContentHandler(handler)
    parser.parse(filename_in)

    with open(filename_out, "w", newline="") as f:
        writer = csv.writer(f)
        for page in handler.page_buffer:
            for line in page:
                writer.writerow(line)

