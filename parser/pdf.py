#!/usr/bin/env python3

from io import StringIO

# Crash Course on pdfminer
#
# Extract text from PDFs like...
#
# ```
# from pdfminer.high_level import extract_text
# with open(filename, "rb") as f:
#   text = extract_text(f)
# ```
#
# The alternative is to use something like...
#
# ```
# from io import StringIO
# from pdfminer.high_level import extract_text_to_fp
# from pdfminer.layout import LAParams
# buffer = StringIO()
# with open(filename, "rb") as f:
#   extract_text_to_fp(f, buffer, laparams=LAParams(), output_type="html", codec=None)
# html = buffer.getvalue()
# ```

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

def parse(filename):
    """Read a binary PDF-encoded file and convert it into an HTML-encoded
    string.
    """
    buffer = StringIO()
    try:
        with open(filename, "rb") as f:
            extract_text_to_fp(f, buffer, laparams=LAParams(), output_type="html", codec=None)
        data = buffer.getvalue()
    finally:
        buffer.close()
    return data

