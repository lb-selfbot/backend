"""
Console utils
"""
from functools import cache

import ansi2html


conv = ansi2html.Ansi2HTMLConverter()


@cache
def ansi_to_html(ansi: str) -> str:
    # Convert ansi to html using the ansi2html library
    return conv.convert(ansi, full=False)
