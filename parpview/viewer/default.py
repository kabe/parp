#!/usr/bin/env python

# Default values

view_columns = (
    ("pr1.funcname", "funcname"),
    ("pr1.ratio", "R1"),
    ("pr1.excl_pe_rank_avg", "excl1"),
    ("pr2.ratio", "R2"),
    ("pr2.excl_pe_rank_avg", "excl2"),
    ("(pr1.excl_pe_rank_avg / pr2.excl_pe_rank_avg)", "speedup"),
    ("pr1.ratio - pr2.ratio", "ratiodiff"),
    ("(pr1.excl_pe_rank_avg - pr2.excl_pe_rank_avg)", "timediff"),
    ("ABS(pr1.ratio - pr2.ratio)", "absratiodiff"),
    )
