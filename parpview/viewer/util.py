#!/usr/bin/env python

import default

def get_graph_attr(graph_style):
    """Get graph attribute.
    
    @param graph_style graph style name of gnuplot
    """
    fillattr = "fs solid 1"
    lineattr = "lw 15"
    pointattr = "ps 15"
    # graph_attrs = {
    #     "boxes": "fs solid 1",
    #     "lines": "lw 15 ps 15",
    #     "points": "lw 15 ps 15",
    #     "linespoint": "lw 15 ps 15",
    #     }
    attrs = []
    if graph_style in default.graph_styles[0]:
        # lines
        attrs.append(lineattr)
        attrs.append(pointattr)
    elif graph_style in default.graph_styles[1]:
        # fill
        attrs.append(lineattr)
        attrs.append(fillattr)
    else:
        raise
    return " ".join(attrs)
