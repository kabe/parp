#!/usr/bin/env python

# Default values


# MPI Application

FUNC_NUM = 10

view_columns = (
    ("pr1.funcname", "funcname"),
    ("pr1.excl_pe_rank_avg", "exectime1"),
    ("pr2.excl_pe_rank_avg", "exectime2"),
    ("(pr1.excl_pe_rank_avg - pr2.excl_pe_rank_avg)", "timediff"),
    ("(pr1.excl_pe_rank_avg / pr2.excl_pe_rank_avg)", "ratio"),
    )

order = "exectime1"

sortmode = "desc"

graph_cols = {
    "y1": ("Ratio1", "Ratio2"),
    "y2": ("exectime1", "exectime2"),}

graph_styles = [
    [
        "lines",
        "dots",
        "steps",
        "errorbars",
        "xerrorbar",
        "xyerrorlines",
        "points",
        "impulses",
        "fsteps",
        "errorlines",
        "xerrorlines",
        "yerrorbars",
        "linespoints",
        "labels",
        "histeps",
        "financebars",
        "xyerrorbars",
        "yerrorlines",],
    [
        "boxes",
        "candlesticks",
        "image",
        "circles",
        "boxerrorbars",
        "filledcurves",
        "rgbimage",
        "boxxyerrorbars",
        "histograms",
        "rgbalpha",
        "pm3d",]
    ]

graph_style = "boxes"


# Workflow

APP_NUM = 10

wfviewcolumns = (
    ("app.name", "Application")
    )
