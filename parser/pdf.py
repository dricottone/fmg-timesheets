#!/usr/bin/env python3

from io import StringIO

from pdfminer.converter import XMLConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams

def parse(filename_in, filename_out):
    """Main routine. Reads a PDF file and writes an XML file."""
    buffer = StringIO()
    manager = PDFResourceManager(caching=False)
    converter = XMLConverter(manager, buffer, laparams=LAParams(), codec=None)
    interpreter = PDFPageInterpreter(manager, converter)

    with open(filename_in, "rb") as f:
        for page in PDFPage.get_pages(f, caching=False):
            interpreter.process_page(page)

    with open(filename_out, "w") as f:
        first = True
        for line in buffer.getvalue().splitlines():
            if not first:
                f.write(line+"\n")
            first = False
        f.write("</pages>\n")

