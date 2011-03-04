#!/usr/bin/env python

# Default values

view_columns = (
    ("pr1.funcname", "funcname"),
    ("pr1.excl_pe_rank_avg", "exectime1"),
    ("pr2.excl_pe_rank_avg", "exectime2"),
    ("(pr1.excl_pe_rank_avg - pr2.excl_pe_rank_avg)", "timediff"),
    ("(pr1.excl_pe_rank_avg / pr2.excl_pe_rank_avg)", "speedup"),
    ("pr1.ratio", "Ratio1"),
    ("pr2.ratio", "Ratio2"),
    ("pr1.ratio - pr2.ratio", "ratiodiff"),
    ("ABS(pr1.ratio - pr2.ratio)", "absratiodiff"),
    )

order = "exectime1"

sortmode = "desc"

graph_cols = {
    "y1": ("Ratio1", "Ratio2"),
    "y2": ("exectime1", "exectime2"),}
