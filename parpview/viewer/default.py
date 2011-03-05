#!/usr/bin/env python

# Default values

view_columns = (
    ("pr1.funcname", "funcname"),
    ("pr1.excl_pe_rank_avg", "exectime1"),
    ("pr2.excl_pe_rank_avg", "exectime2"),
    ("(pr1.excl_pe_rank_avg - pr2.excl_pe_rank_avg)", "timediff"),
    ("(pr1.excl_pe_rank_avg / pr2.excl_pe_rank_avg)", "speedup"),
    ("pr1.excl_avg_ratio", "Ratio1"),
    ("pr2.excl_avg_ratio", "Ratio2"),
    ("pr1.excl_avg_ratio - pr2.excl_avg_ratio", "ratiodiff"),
    ("ABS(pr1.excl_avg_ratio - pr2.excl_avg_ratio)", "absratiodiff"),
    )

order = "exectime1"

sortmode = "desc"

graph_cols = {
    "y1": ("Ratio1", "Ratio2"),
    "y2": ("exectime1", "exectime2"),}
