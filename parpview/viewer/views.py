# Create your views here.
from django.http import HttpResponse, HttpResponseServerError
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from parpview.viewer.models import ViewParam

import resource
import math
import time
import string
import subprocess
import cPickle
import json
import operator
import decimal

import sys
import os
import os.path
relpath = "../../"
path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    relpath)
if path not in sys.path:
    sys.path.append(path)

import yaml
import pyodbc

import tau.util
import tau.db
import tau.nm.loader
import tau.TauLoad.Loader
import config.db

import default
import memcachedwrapper
import getraw
import hashutil
import tableutil

# GXPmake

# Support Class
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


# Memcached Preparation
use_memcache = True
memcached_conn = memcachedwrapper.MemcachedConnection(use_memcache,
                                                      ['127.0.0.1:11211'])
print memcached_conn
# YAML
e9n_function = "viewer/e9n/function.yaml"

def helloworld(request):
    #return HttpResponse("Hello World")
    return HttpResponseRedirect("/pgdiff/1/1/")


def pgd1_dummy(request):
    """redirector
    
    Arguments:
    - `request`:
    """
    return HttpResponseRedirect("/pgd1/ratiodiff/desc/ratio/1/7/")


def pgd2_dummy(request):
    """redirector
    
    Arguments:
    - `request`:
    """
    return HttpResponseRedirect("/pgd2/desc/")


@cache_page(60 * 5)
def pgroupdiff(request, pg1, pg2):
    """Show ProfGroup difference.

    @param request request object
    @param pg1 ProfGroup ID 1 (which should be visualized left)
    @param pg2 ProfGroup ID 2 (which should be visualized right)
    """
    view_meter_diffratio_max = 10
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    time1 = time.time()
    params = ViewParam.objects.get()
    dbtype = params.dbtype
    if dbtype == "sqlite3":
        conn = tau.db.init("sqlite3", dbfile=params.sqlite3_file)
    elif dbtype == "postgres":
        conn = tau.db.init("postgres", username="kabe", hostname="127.0.0.1")
    else:
        return HttpResponseServerError(content="Cannot connect to the database")
    # Param
    stranger_diff_thresh = params.susp_thresh
    t_params = {"stranger_diffpercent_thresh": stranger_diff_thresh * 100,
                "stranger_diffpercent_thresh_neg": -stranger_diff_thresh * 100,
                "susp_ratio_thresh": params.susp_ratio_thresh * 100,
                "vmdfrmax": view_meter_diffratio_max,
                }
    # Main comparation
    sql = """
SELECT pr1.funcname,
       pr1.ratio AS R1,
       pr1.excl_pe_rank_avg AS excl1,
       pr2.ratio AS R2,
       pr2.excl_pe_rank_avg AS excl2,
       (pr2.ratio - pr1.ratio) * 100 AS ratiodiff,
       (pr2.excl_pe_rank_avg - pr1.excl_pe_rank_avg) AS timediff,
       ABS(pr2.ratio - pr1.ratio) * 100 AS absratiodiff
FROM (SELECT * FROM pgroup_ratio WHERE profgroup_id = ?) pr1,
     (SELECT * FROM pgroup_ratio WHERE profgroup_id = ?) pr2
WHERE pr1.funcname = pr2.funcname
ORDER BY ABS(pr2.ratio - pr1.ratio) DESC
;
"""
    r_main = ()
    r1_max, r2_max = 0, 0
    if pg1 != pg2:
        r_main = conn.select(sql, (pg1, pg2))
        r1_max, r2_max = max(x[2] for x in r_main), max(x[4] for x in r_main)
    # New comparison
    newc_colnames = ("PG L", "PG R",
                     "Application", "Place", "# of nodes",
                     "# of Processes", "Library", "Avg. Time", "StdDev.",
                     "PG L2", "PG R2")
    newc = """
SELECT pg.id,
       pg.application,
       pg.place,
       pg.nodes,
       pg.procs,
       pg.library,
       pgm.avg_time,
       pgm.var
FROM profgroup AS pg,
     pgroup_meta AS pgm
WHERE pg.id = pgm.profgroup_id
ORDER BY pg.id
;
"""
    r_newc = conn.select(newc)
    # stddev
    r_newc2 = (r[0:-1] + (math.sqrt(r[-1]),) for r in r_newc)
    #print r_newc2
    # Log
    ru2 = resource.getrusage(resource.RUSAGE_SELF)
    time2 = time.time()
    rd = (ru2.ru_utime - ru1.ru_utime,
          ru2.ru_stime - ru1.ru_stime,
          ru2.ru_inblock - ru1.ru_inblock,
          ru2.ru_oublock - ru1.ru_oublock,
          time2 - time1,
          )
    return render_to_response('pgdiff.html',
                              {"params": t_params,
                               "pg1": int(pg1),
                               "pg2": int(pg2),
                               "result": r_main,
                               "rnc_n": newc_colnames,
                               "rnc": r_newc2,
                               "rd": rd,
                               "pg_maxs": (r1_max, r2_max)
                               })


def pgdiff2(request, params):
    """Test funtion for form paramteres.
    
    @param request request object
    @param params get parameters
    """
    return HttpResponseRedirect(reverse('parpview.viewer.pgdiff'), args=(1, 1))


def pgview(request, pg_id):
    """Detail view of ProfGroup.

    @param request request object
    @param pg_id ProfGroup ID
    """
    # Log
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    time1 = time.time()
    # Params
    params = ViewParam.objects.get()
    dbtype = params.dbtype
    if dbtype == "sqlite3":
        conn = tau.db.init("sqlite3", dbfile=params.sqlite3_file)
    elif dbtype == "postgres":
        conn = tau.db.init("postgres", username="kabe", hostname="127.0.0.1")
    else:
        raise Http404
    # Main comparation
    pg_sql = """
SELECT pg.application AS app,
       pg.nodes AS nodes,
       pg.procs AS procs,
       pg.place AS place,
       pg.library AS library
FROM profgroup AS pg
WHERE pg.id = ?
;
"""
    r_pg = conn.select(pg_sql, (pg_id,))[0]
    pgpe_sql = """
SELECT pe.id AS pe_id,
       pe.exec_time AS etime,
       pe.start_ts AS start_ts
FROM profgroup AS pg,
     profexec AS pe
WHERE pg.id = pe.profgroup_id
  AND pg.id = ?
ORDER BY pe_id
;
"""
    r_pgpe = conn.select(pgpe_sql, (pg_id,))
    # Log
    ru2 = resource.getrusage(resource.RUSAGE_SELF)
    time2 = time.time()
    rd = (ru2.ru_utime - ru1.ru_utime,
          ru2.ru_stime - ru1.ru_stime,
          ru2.ru_inblock - ru1.ru_inblock,
          ru2.ru_oublock - ru1.ru_oublock,
          time2 - time1,
          )
    return render_to_response('pgdetail.html',
                              {"pg_id": pg_id,
                               "r_pg": r_pg,
                               "r_pgpe": r_pgpe,
                               "pe_num": len(r_pgpe),
                               "rd": rd,
                               })


#@cache_page(60 * 1)
def pgd1(request, order, sortmode, graphmode, pg1, pg2):
    """Show ProfGroup difference.

    @param request
    @param order
    @param sortmode
    @param graphmode
    @param pg1
    @param pg2
    """
    view_meter_diffratio_max = 10.0
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    time1 = time.time()
    params = ViewParam.objects.get()
    dbtype = params.dbtype
    if dbtype == "sqlite3":
        conn = tau.db.init("sqlite3", dbfile=params.sqlite3_file)
    elif dbtype == "postgres":
        conn = tau.db.init("postgres", username="kabe", hostname="127.0.0.1")
    else:
        raise Http404
    ## Param
    stranger_diff_thresh = params.susp_thresh
    t_params = {"stranger_diffpercent_thresh": stranger_diff_thresh * 100,
                "stranger_diffpercent_thresh_neg": -stranger_diff_thresh * 100,
                "susp_ratio_thresh": params.susp_ratio_thresh * 100,
                "vmdfrmax": view_meter_diffratio_max,
                }
    ## Sort order
    if order == "timediff":
        order_str = "ABS(pr1.excl_pe_rank_avg - pr2.excl_pe_rank_avg)"
    elif order == "speedup":
        order_str = "ABS(pr1.excl_pe_rank_avg / pr2.excl_pe_rank_avg)"
    elif order == "ratiodiff":
        order_str = "ABS(pr1.ratio - pr2.ratio)"
    else:
        raise Http404
    ## Sort mode
    if sortmode == "asc":
        order_str += " ASC"
    elif sortmode == "desc":
        order_str += " DESC"
    else:
        raise Http404
    ## Main comparation
    sql = """
SELECT pr1.funcname,
       pr1.ratio AS R1,
       pr1.excl_pe_rank_avg AS excl1,
       pr2.ratio AS R2,
       pr2.excl_pe_rank_avg AS excl2,
       (pr1.excl_pe_rank_avg / pr2.excl_pe_rank_avg) AS speedup,
       (pr1.ratio - pr2.ratio) * 100 AS ratiodiff,
       (pr1.excl_pe_rank_avg - pr2.excl_pe_rank_avg) AS timediff,
       ABS(pr1.ratio - pr2.ratio) * 100 AS absratiodiff
FROM (SELECT * FROM pgroup_ratio WHERE profgroup_id = ?) pr1,
     (SELECT * FROM pgroup_ratio WHERE profgroup_id = ?) pr2
WHERE pr1.funcname = pr2.funcname
ORDER BY ${order}
;
"""
    sql_tpl = string.Template(sql)
    sql_str = sql_tpl.substitute(order=order_str)
    r_main = ()
    r1_max, r2_max = 0, 0
    if pg1 != pg2:
        mc_index = "diff_%s" % (sql_str)
        trycache = memcached_conn.get(mc_index)
        if trycache:
            r_main = cPickle.loads(trycache)
            print "Cached"
        else:
            r_main = conn.select(sql_str, (pg1, pg2))
            cachestr = cPickle.dumps(r_main)
            memcached_conn.set(mc_index, cachestr)
        r1_max, r2_max = max(x[2] for x in r_main), max(x[4] for x in r_main)
    ## New comparison
    newc_colnames = ("PG L", "PG R",
                     "Application", "Place", "# of nodes",
                     "# of Processes", "Library", "Avg. Time", "StdDev.",
                     "PG L2", "PG R2")
    newc = """
SELECT pg.id,
       pg.application,
       pg.place,
       pg.nodes,
       pg.procs,
       pg.library,
       pgm.avg_time,
       pgm.var
FROM profgroup AS pg,
     pgroup_meta AS pgm
WHERE pg.id = pgm.profgroup_id
ORDER BY pg.id
;
"""
    r_newc = conn.select(newc)
    ## stddev
    r_newc2 = (r[0:-1] + (math.sqrt(r[-1]),) for r in r_newc)
    #print r_newc2
    ## Log
    ru2 = resource.getrusage(resource.RUSAGE_SELF)
    time2 = time.time()
    rd = (ru2.ru_utime - ru1.ru_utime,
          ru2.ru_stime - ru1.ru_stime,
          ru2.ru_inblock - ru1.ru_inblock,
          ru2.ru_oublock - ru1.ru_oublock,
          time2 - time1,
          )
    imagefilename = gengraph(pg1, pg2, graphmode, r_main)
    return render_to_response('pgd1.html',
                              {"params": t_params,
                               "pg1": int(pg1),
                               "pg2": int(pg2),
                               "result": r_main,
                               "rd": rd,
                               "pg_maxs": (r1_max, r2_max),
                               "imgfilename": imagefilename,
                               "reqparams": {"graphmode": graphmode,
                                             "order": order,
                                             "sortmode": sortmode,}
                               })


def pgd2(request, sortmode):
    """Show ProfGroup difference.

    @param request
    @param sortmode
    """
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    time1 = time.time()
    params = ViewParam.objects.get()
    dbtype = params.dbtype
    if dbtype == "sqlite3":
        conn = tau.db.init("sqlite3", dbfile=params.sqlite3_file)
    elif dbtype == "postgres":
        conn = tau.db.init("postgres", username="kabe", hostname="127.0.0.1")
    else:
        return HttpResponseServerError("Cannot connect to the database")
    ##########################
    ##### New comparison #####
    ##########################
    newc_colnames = ("PG 1", "PG 2",
                     "Application", "Comment", "Place",
                     "# of nodes", "# of Processes",
                     "Avg. Time [sec]", "StdDev. [sec]",)
    newc = """
SELECT pg.id,
       pg.application,
       pg.place,
       pg.nodes,
       pg.procs,
       pg.library,
       pg.app_viewname,
       pgm.avg_dtime,
       pgm.dvar
FROM profgroup AS pg,
     pgroup_meta AS pgm
WHERE pg.id = pgm.profgroup_id
ORDER BY pg.app_viewname, pg.place, pg.id
;
"""
    r_newc = conn.select(newc)
    #print r_newc
    ## stddev
    r_newc2 = (r[0:-1] + (math.sqrt(r[-1]),) for r in r_newc)
    ###################
    ##### Request #####
    ###################
    ## Request mode
    graph_cols = {"y1": [], "y2": []}
    pgs = []
    if request.method == "POST":
        print "POST Parameters:"
        print request.POST
        graph_cols["y1"] = request.POST.getlist("graph_y1")
        graph_cols["y2"] = request.POST.getlist("graph_y2")
        pgs = [request.POST["pg1"], request.POST["pg2"]]
        ##### Column definitions #####
        existing_usecol_indeces = request.POST.getlist("use_flag")
        existing_usecols = tuple((request.POST["coldef_%s" % (ind)],
                                  request.POST["colname_%s" % (ind)])
                                 for ind in existing_usecol_indeces)
        print "existing_usecols:"
        print existing_usecols
        new_usecol_indeces = request.POST.getlist("use_flag_new")
        new_usecols = tuple((request.POST["new_coldef_%s" % (ind)],
                             request.POST["new_colname_%s" % (ind)])
                            for ind in new_usecol_indeces)
        print "new_usecol"
        print new_usecols
        view_columns = existing_usecols + new_usecols
        ## Order
        post_order_idx = int(request.POST["order"])
        order = view_columns[post_order_idx][1]
    else:  # default mode
        graph_cols = default.graph_cols
        pgs = [1, 1]
        view_columns = default.view_columns
        order = default.order
        #sortmode = default.sortmode
    print "pgs: %s" % (pgs)
    col_0, col_1 = ([x for x in r_newc
                     if int(x[0]) == int(pgs[0])][0],
                    [x for x in r_newc
                     if int(x[0]) == int(pgs[1])][0])
    print col_0, col_1
    if col_0[6] != col_1[6]:
        raise Exception("Impossible to compare two different applications")
    print "Graph Parameters:"
    print graph_cols
    #print request.META
    ## Param
    t_params = {}
    coldef_params = {}
    coldef_params["newcols"] = [x for x in xrange(5)]  # new columns defs
    ##### Main comparison SQL generation #####
    # define view columns
    ## dictionary of strings tuple: (key, value) = (definition, name)
    view_columns_joined_str = ", ".join(" AS ".join(vc)
                                        for vc in view_columns)
    #print view_columns_joined_str
    checked_radios = determine_checked_radios(view_columns, graph_cols)
    ## Joined tables (or views) definitions
    joined_tables = (
        ("(SELECT * FROM pgroup_ratio WHERE profgroup_id = ?)", "pr1"),
        ("(SELECT * FROM pgroup_ratio WHERE profgroup_id = ?)", "pr2"),
        )
    joined_tables_joined_str = ", ".join(" ".join(jt) for jt in joined_tables)
    ## Join conditions
    join_conditions = [
        "pr1.funcname = pr2.funcname",
        ]
    join_conditions_joined_str = " AND ".join(join_conditions)
    ## Sort order
    column_names = (x[1] for x in view_columns)
    if order not in column_names:
        return HttpResponseServerError(content="Order %s not in columns" % (order))
    order_str = order
    ## Sort mode
    if sortmode == "asc":
        order_str += " ASC"
    elif sortmode == "desc":
        order_str += " DESC"
    else:
        return HttpResponseServerError(content="Order mode not in list")
    ## Prepare YAML
    y = None
    try:
        with open(e9n_function) as f:
            s = f.read()
            y = yaml.load(s)
    except Exception, e:
        raise e
    ## Query
    # @TODO What should be the definition of "from" and join condition?
    # should it be able to be specified by a user?
    sql = """
SELECT ${columns}
FROM ${tables}
WHERE ${join_conditions}
ORDER BY ${order}
;
"""
    sql_tpl = string.Template(sql)
    sql_str = sql_tpl.substitute(columns=view_columns_joined_str,
                                 tables=joined_tables_joined_str,
                                 join_conditions=join_conditions_joined_str,
                                 order=order_str,)
    #print sql_str
    r_main = ()
    appviewname = col_0[6]
    #print r_newc[int(pgs[0]) - 1][6], r_newc[int(pgs[1]) - 1][6]
    functip = {}
    if pgs[0] != pgs[1]:
        mc_index = hashutil.md5(sql_str + str(pgs[0]) + "_" + str(pgs[1]))
        trycache = memcached_conn.get(mc_index)
        if trycache:
            r_main = cPickle.loads(trycache)
        else:
            r_main = conn.select(sql_str, (pgs[0], pgs[1]))
            r_main = tableutil.remove_unnecessary_funcs(r_main, appviewname, y)
            cachestr = cPickle.dumps(r_main)
            memcached_conn.set(mc_index, cachestr)
        ## Function Comments Tooltip
        try:
            functip = y[appviewname]
        except KeyError:
            functip = {}
    ### Graph generation
    imagefilename = ""
    graphtitle = "Column for graph unspecified"
    if pgs[0] != pgs[1]:
        try:
            graphtitle, imagefilename = gengraph(pgs[0], pgs[1], r_main, order,
                                                 view_columns, graph_cols)
        except Exception, e:
            pass
    ## Schema Info
    vschema = conn.getschema("pgroup_ratio")
    ## Log
    ru2 = resource.getrusage(resource.RUSAGE_SELF)
    time2 = time.time()
    rd = (ru2.ru_utime - ru1.ru_utime,
          ru2.ru_stime - ru1.ru_stime,
          ru2.ru_inblock - ru1.ru_inblock,
          ru2.ru_oublock - ru1.ru_oublock,
          time2 - time1,
          )
    return render_to_response('pgd2.html',
                              {"self_path": request.path,
                               "params": t_params,
                               "cols": view_columns,
                               "pg1": int(pgs[0]),
                               "pg2": int(pgs[1]),
                               "result": r_main,
                               "rnc_n": newc_colnames,
                               "rnc": r_newc2,
                               "rd": rd,
                               "imgfilename": imagefilename,
                               "reqparams": {"order": order,
                                             "sortmode": sortmode,
                                             "path": request.path,},
                               "checked_radios": checked_radios,
                               "coldef_params": coldef_params,
                               "graph_title": graphtitle,
                               "vschema": vschema,
                               "functip": functip,
                               })


def pgd3(request, sortmode):
    """Show ProfGroup difference.

    @param request
    @param sortmode
    """
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    time1 = time.time()
    params = ViewParam.objects.get()
    dbtype = params.dbtype
    if dbtype == "sqlite3":
        conn = db.init("sqlite3", dbfile=params.sqlite3_file)
    elif dbtype == "postgres":
        conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
    else:
        return HttpResponseServerError("Cannot connect to the database")

    ##########################
    ##### New comparison #####
    ##########################

    newc_colnames = ("PG 1", "PG 2",
                     "Application", "Comment", "Place",
                     "# of nodes", "# of Processes",
                     "Avg. Time [sec]", "StdDev. [sec]",)
    newc = """
SELECT pg.id,
       pg.application,
       pg.place,
       pg.nodes,
       pg.procs,
       pg.library,
       pg.app_viewname,
       pgm.avg_dtime,
       pgm.dvar
FROM profgroup AS pg,
     pgroup_meta AS pgm
WHERE pg.id = pgm.profgroup_id
ORDER BY pg.app_viewname, pg.place, pg.id
;
"""
    r_newc = conn.select(newc)
    #print r_newc

    ## stddev (replace the last column of r_newc with sqrted value)

    r_newc2 = [r[0:-1] + (math.sqrt(r[-1]),) for r in r_newc]

    ###################
    ##### Request #####
    ###################

    ## Request mode

    graph_cols = {"y1": [], "y2": []}
    pgs = []
    if request.method == "POST":
        print "POST Parameters:"
        print request.POST
        graph_cols["y1"] = request.POST.getlist("graph_y1")
        graph_cols["y2"] = request.POST.getlist("graph_y2")
        pgs = [int(request.POST["pg1"]), int(request.POST["pg2"])]

        ##### Column definitions #####

        existing_usecol_indeces = request.POST.getlist("use_flag")
        existing_usecols = tuple((request.POST["coldef_%s" % (ind)],
                                  request.POST["colname_%s" % (ind)])
                                 for ind in existing_usecol_indeces)
        print "existing_usecols:"
        print existing_usecols
        new_usecol_indeces = request.POST.getlist("use_flag_new")
        new_usecols = tuple((request.POST["new_coldef_%s" % (ind)],
                             request.POST["new_colname_%s" % (ind)])
                            for ind in new_usecol_indeces)
        print "new_usecol"
        print new_usecols
        view_columns = existing_usecols + new_usecols

        ## Order

        post_order_idx = int(request.POST["order"])
        order = view_columns[post_order_idx][1]
    else:  # default mode
        graph_cols = default.graph_cols
        pgs = [1, 1]
        view_columns = default.view_columns
        order = default.order
        #sortmode = default.sortmode
    print "pgs: %s" % (str(pgs))
    col_0, col_1 = ([x for x in r_newc
                     if int(x[0]) == int(pgs[0])][0],
                    [x for x in r_newc
                     if int(x[0]) == int(pgs[1])][0])
    print col_0, col_1
    if col_0[6] != col_1[6]:
        raise Exception("Impossible to compare two different applications")

    # Execution Time

    experiment_exec_times = [col_0[7], col_1[7]]
    print "Exec time: %s" % (experiment_exec_times)

    #print "Graph Parameters:"
    #print graph_cols

    ## Param

    #print request.META
    t_params = {}
    coldef_params = {}
    coldef_params["newcols"] = [x for x in xrange(5)]  # new columns defs

    ##### Main comparison SQL generation #####
    # define view columns
    ## dictionary of strings tuple: (key, value) = (definition, name)

    view_columns_joined_str = ", ".join(" AS ".join(vc)
                                        for vc in view_columns)
    #print view_columns_joined_str
    checked_radios = determine_checked_radios(view_columns, graph_cols)

    ## Joined tables (or views) definitions

    joined_tables = (
        ("(SELECT * FROM pgroup_ratio WHERE profgroup_id = ?)", "pr1"),
        ("(SELECT * FROM pgroup_ratio WHERE profgroup_id = ?)", "pr2"),
        )
    joined_tables_joined_str = ", ".join(" ".join(jt) for jt in joined_tables)

    ## Join conditions

    join_conditions = [
        "pr1.funcname = pr2.funcname",
        ]
    join_conditions_joined_str = " AND ".join(join_conditions)

    ## Sort order

    column_names = (x[1] for x in view_columns)
    if order not in column_names:
        return HttpResponseServerError(content="Order %s not in columns" % \
                                           (order))
    order_str = order

    ## Sort mode

    if sortmode == "asc":
        order_str += " ASC"
    elif sortmode == "desc":
        order_str += " DESC"
    else:
        return HttpResponseServerError(content="Order mode not in list")

    ## Prepare YAML

    y = None
    try:
        with open(e9n_function) as f:
            s = f.read()
            y = yaml.load(s)
    except Exception, e:
        raise e

    ## Query
    # @TODO What should be the definition of "from" and join condition?
    # should it be able to be specified by a user?

    sql = """
SELECT ${columns}
FROM ${tables}
WHERE ${join_conditions}
ORDER BY ${order}
;
"""
    sql_tpl = string.Template(sql)
    sql_str = sql_tpl.substitute(columns=view_columns_joined_str,
                                 tables=joined_tables_joined_str,
                                 join_conditions=join_conditions_joined_str,
                                 order=order_str,)
    #print sql_str
    r_main = ()
    appviewname = col_0[6]
    #print r_newc[int(pgs[0]) - 1][6], r_newc[int(pgs[1]) - 1][6]
    functip = {}
    if pgs[0] != pgs[1]:
        mc_index = hashutil.md5(sql_str + str(pgs[0]) + "_" + str(pgs[1]))
        trycache = memcached_conn.get(mc_index)
        if trycache:
            r_main = cPickle.loads(trycache)
        else:
            r_main = conn.select(sql_str, (pgs[0], pgs[1]))
            r_main = tableutil.remove_unnecessary_funcs(r_main, appviewname, y)
            cachestr = cPickle.dumps(r_main)
            memcached_conn.set(mc_index, cachestr)

        ## Function Comments Tooltip

        try:
            functip = y[appviewname]
        except KeyError:
            functip = {}

    ### 2011/04/29 Special Order
    ## Re-Ordering
    ### by t1 * log(t1 / t2)
    ### t1 = x[1], t2 = x[2]

    r_main = sorted(r_main,
                    lambda x, y: cmp(x[1] * math.log(x[1] / x[2]),
                                     y[1] * math.log(y[1] / y[2])),
                    None,
                    True)
    r_main = tableutil.add_column(r_main,
                                  [math.log(x[1]) * math.log(x[1] / x[2])
                                   for x in r_main])
    r_main = tableutil.add_column(r_main,
                                  [x[1] * math.log(x[1] / x[2])
                                   for x in r_main])

    ### Graph generation

    imagefilename = ""
    graphtitle = "Column for graph unspecified"
    if pgs[0] != pgs[1]:
        try:
            graphtitle, imagefilename = gengraph(pgs[0], pgs[1], r_main, order,
                                                 view_columns, graph_cols)
        except Exception, e:
            pass

    ## Schema Info

    vschema = conn.getschema("pgroup_ratio")

    ## Log

    ru2 = resource.getrusage(resource.RUSAGE_SELF)
    time2 = time.time()
    rd = (ru2.ru_utime - ru1.ru_utime,
          ru2.ru_stime - ru1.ru_stime,
          ru2.ru_inblock - ru1.ru_inblock,
          ru2.ru_oublock - ru1.ru_oublock,
          time2 - time1,
          )

    # Render All

    return render_to_response('pgd2.html',
                              {"self_path": request.path,
                               "params": t_params,
                               "cols": view_columns,
                               "pg1": int(pgs[0]),
                               "pg2": int(pgs[1]),
                               "result": r_main,
                               "rnc_n": newc_colnames,
                               "rnc": r_newc2,
                               "rd": rd,
                               "imgfilename": imagefilename,
                               "reqparams": {"order": order,
                                             "sortmode": sortmode,
                                             "path": request.path,},
                               "checked_radios": checked_radios,
                               "coldef_params": coldef_params,
                               "graph_title": graphtitle,
                               "vschema": vschema,
                               "functip": functip,
                               })


##################################################
###                 Workflows                  ###
##################################################

@cache_page(60 * 5)
def wf(request,):
    """Workflow Trial diff.

    @param Django request object
    """
    cstr = config.db.connect_str
    conn = pyodbc.connect(config.db.connect_str)
    cursor = conn.cursor()
    # List workflows
    cursor.execute("""
SELECT id, name
FROM workflow
ORDER BY name, id
""")
    wfs = cursor.fetchall()

    return render_to_response(
        'wf.html',
        {
            "self_path": request.path,
            "wfs": wfs,})


@cache_page(60 * 5)
def workflow_info(request, wf):
    """Workflow Information.

    @param Django request object
    @param wf workflow id
    """
    cstr = config.db.connect_str
    conn = pyodbc.connect(config.db.connect_str)
    cursor = conn.cursor()
    cursor.execute("""
SELECT name FROM workflow WHERE id=?
""", wf)
    workflow = cursor.fetchone()
    cursor.execute("""
SELECT id, name FROM application
WHERE workflow=?
""", wf)
    apps = cursor.fetchall()
    
    cursor.execute("""
SELECT
  wft.id id,
  wf.name name,
  wft.workflow_condition wf_condition,
  wfc.location location,
  wfc.filesystem filesystem,
  wfc.worker_num worker_num,
  AVG(wft.elapsed_time) elapsed
FROM
  workflow_trial AS wft,
  workflow AS wf,
  workflow_condition AS wfc
WHERE
  wf.id = wft.workflow AND
  wfc.id = wft.workflow_condition AND
  wf.id = ?
GROUP BY wft.workflow_condition
""", wf)
    conds = cursor.fetchall()

    return render_to_response(
        'workflowinfo.html',
        {
            "self_path": request.path,
            "workflow": workflow,
            "conds": conds,
            "apps": apps,})


def wfdiff(request, wf, wfc1, wfc2):
    """Print diff.

    @param request request object
    @param wf workflow id
    @param wft_1 Workflow condition ID 1
    @param wft_2 Workflow condition ID 2
    """
    cstr = config.db.connect_str
    conn = pyodbc.connect(config.db.connect_str)
    cursor = conn.cursor()
    # Get workflow obj
    workflow = cursor.execute(
        "SELECT * FROM workflow WHERE id = ?", wf).fetchone()
    print "workflow"
    print workflow
    #
    sql, columns_fixed, columns, sqlparams = construct_wfdiff_sql(
        request, wf, wfc1, wfc2)
    print sql
    cursor.execute(sql, *sqlparams)
    drows = cursor.fetchall()
    print drows
    jsoninfo = generate_wf_graph_json(drows, columns_fixed + columns, None)
    print jsoninfo
    jsondata = json.dumps(jsoninfo, cls=DecimalEncoder)
    return render_to_response(
        'wfd.html',
        {
            "self_path": request.path,
            "sql": sql,
            "columnsf": columns_fixed,
            "columns": columns,
            "drows": drows,
            "jsondata": jsondata,
            "workflow": workflow,
            })


##################################################
###                 Utilities                  ###
##################################################


def gengraph(index_A, index_B, funcs, order, colinfo, cols):
    """Generate GNUPLOT Graph.
    
    @param index_A index for A
    @param index_B index for B
    @param funcs
    @param order sort order column name
    @param colinfo names of columns
    @param cols column names of y1 and y2
    """
    graph_width = 4
    plot_template = """reset
set terminal postscript eps enhanced color "Gothic-BBB-EUC-H" 112
set size 6
set output "out.eps"
${setgrid}
set key above
${y1label}
${y2label}
${xtics_conf}
set xtics rotate
${y2tics}
plot \
    ${plines}
"""
    pl_template = '"${datafile}" using ($1${goffset}):${col_index}:(${gwidth})' \
        ' title "${colname}" w boxes fs solid 1 axis ${axis}'
    template = string.Template(plot_template)
    pltemplate = string.Template(pl_template)
    # Determine image file name
    cur_time = time.time()
    image_filename = str(cur_time) + ".png"
    # Graph title
    # title = "%s \\n (order %s)" % \
    #     (", ".join(cols["y1"]  + cols["y2"]).replace("_", "\\\\_"), order)
    title = "";  # "Order by %s" % (order)
    y1label = "set ylabel \"%s\"" % (", ".join(cols["y1"]).replace("_", "\\\\_"))
    y2label = "set y2label \"%s\"" % (", ".join(cols["y2"]).replace("_", "\\\\_"))
    y2tics = "set y2tics"
    # Graph scale calc
    graph_interval = 4 * (len(cols["y1"]) + len(cols["y2"])) + 4
    print "Graph Interval = %d" % (graph_interval)
    # xtics
    xtics_t = "set xtics(${conf})"
    xtics_tt = string.Template(xtics_t)
    xtics_list = []  # will be a function name list
    timedata = ""
    for i, t in enumerate(funcs):
        goffset = i * graph_interval
        #print i, t
        if i >= 10: break
        ts = "%d " % (goffset) + " ".join(str(x) for x in t) + "\n"
        timedata += ts
        xtics_list.append('"' + t[0][:-2] + '"' + " " + str(i * graph_interval))
    tmpfilename = os.tmpnam()
    xtics_conf = xtics_tt.substitute(
        conf=",".join(xtics_list).replace("_", "\\\\_"))
    # make plines
    lines = {"y1": "", "y2": ""}
    ## X
    ss = []
    for i, valcolumn in enumerate(cols["y1"]):
        graph_offset = graph_width * (i + 0.5) - \
            ((graph_interval - graph_width / 2) / 2)
        ss.append(pltemplate.safe_substitute(
                col_index=str([x[1] for x in colinfo].index(valcolumn) + 2),
                axis="x1y1",
                datafile=tmpfilename,
                goffset="%+d" % (graph_offset),
                gwidth=graph_width,
                colname=valcolumn,))
    lines["y1"] = ", ".join(ss)
    ## Y
    ss = []
    for i, valcolumn in enumerate(cols["y2"]):
        k = i + len(cols["y1"])
        graph_offset = graph_width * (k + 0.5) - \
            ((graph_interval - graph_width / 2) / 2)
        ss.append(pltemplate.safe_substitute(
                col_index=str([x[1] for x in colinfo].index(valcolumn) + 2),
                axis="x1y2",
                datafile=tmpfilename,
                goffset="%+d" % (graph_offset),
                gwidth=graph_width,
                colname=valcolumn,))
    lines["y2"] = ", ".join(ss)
    setgrid = ""
    if lines["y1"] and lines["y2"]:
        plines = ", ".join(lines.values())
    elif lines["y1"]:
        setgrid = "set grid"
        plines = lines["y1"]
        y2label = ""
        y2tics = ""
    elif lines["y2"]:
        setgrid = "set grid"
        plines = lines["y2"]
        y1label = ""
    else:
        #return HttpResponseServerError(content="Graph generation: lines error")
        raise Exception("Nothing to display in graph")
    # Main
    s = template.safe_substitute(title=title,
                                 datafile=tmpfilename,
                                 xtics_conf=xtics_conf,
                                 setgrid=setgrid,
                                 plines=plines,
                                 y1label=y1label,
                                 y2label=y2label,
                                 y2tics=y2tics,)
    with open(tmpfilename, "w") as f:
        f.write(timedata.strip())
        f.close()
        sp = subprocess.Popen(("gnuplot",), stdin=subprocess.PIPE)
        sp.stdin.write(s)
        sp.stdin.close()
        sp.wait()
        sp2 = subprocess.Popen(("convert",
                                "out.eps",
                                os.path.join("viewer", "data", image_filename)))
        sp2.wait()
    try:
        os.unlink(tmpfilename)
    except:
        pass
    print "DONE"
    return title, image_filename


def determine_checked_radios(cols, graphcols):
    """
    @param cols Columns for rendering a table
    @param graphcols Columns dictionary of checked columns
    """
    d = {"y1": None, "y2": None}
    print "cols:"
    print cols
    print "graphcols:"
    print graphcols
    # Init
    for y in d.keys():
        d[y] = []
        for i, col in enumerate(cols):
            d[y].append("")
    # Toggle
    for y in d.keys():
        for col in graphcols[y]:
            try:
                index = [x[1] for x in cols].index(col)
            except:
                index = 0
            d[y][index] = 'checked="checked"'
    return d


def construct_wfdiff_sql(request, wf, wfc1, wfc2):
    """Construct SQL for comparing Workflow trials.

    @param request
    @param wf workflow ID
    @param wfc1 workflow condition id 1
    @param wfc2 workflow condition id 2
    """
    columns_fixed = (("app.name", "ApplicationName"),
                     ("cv1.elapsed_local", "ElapsedL1"),
                     ("cv2.elapsed_local", "ElapsedL2"))
    # TODO: configure columns using request argument
    columns = (("cv1.elapsed_remote", "ElapsedR1"),
               ("cv2.elapsed_remote", "ElapsedR2"),
               ("cv1.time_user", "UTime1"),
               ("cv2.time_user", "UTime2"),
               ("cv1.time_system", "STime1"),
               ("cv2.time_system", "STime2"),
               ("cv1.minor_faults", "MinFlt1"),
               ("cv2.minor_faults", "MinFlt2"),
               ("cv1.major_faults", "MajFlt1"),
               ("cv2.major_faults", "MajFlt2"),)
    sql_columns = ", ".join(
        " ".join((col[0], col[1]))
        for col in columns_fixed + columns)
    # TODO: Check the SQL sentence is valid/secure.
    sql = """
SELECT
  %s
FROM
  condition_view cv1,
  condition_view cv2,
  application app
WHERE
  cv1.application = cv2.application AND
  cv1.workflow = cv2.workflow AND
  cv1.wf_condition = ? AND
  cv2.wf_condition = ? AND
  cv1.application = app.id AND
  cv1.workflow = ?
""" % (sql_columns)
    return sql, columns_fixed, columns, (wfc1, wfc2, wf)


def generate_wf_graph_json(contents, columns, graph_cols):
    """Genearte JSON string to create a graph.

    @param contents all column contents
    @param columns column names
    @param graph_cols graph column names (Dict of for y1, y2)
    """
    series = []
    contents_to_appmap = {}
    for i, column in enumerate(columns):
        contents_to_appmap[column[1]] = tuple(map(
                operator.itemgetter(i), contents))[0: default.APP_NUM]
    #print "contents_to_appmap"
    #print contents_to_appmap
    # Fixed graph columns
    graph_cols = {"y1": ("ElapsedL1", "ElapsedL2",
                         "ElapsedR1", "ElapsedR2",
                         "UTime1", "UTime2", "STime1", "STime2",),
                  "y2": ("MinFlt1", "MinFlt2",)}
    # ApplicationName s
    categories = tuple(content[0] for content in contents)[0:default.APP_NUM]
    # Values
    yaxis = []
    axis_idx = 0
    for axis in ("y1", "y2",):
        if axis in graph_cols.keys():
            yaxis.append({
                    "title": {"align": "middle",
                              "text": ", ".join(graph_cols[axis]),},
                    # Odd-number axis will be placed right
                    "opposite": True if axis_idx % 2 else False})
            for col in graph_cols[axis]:
                series.append(
                    {
                        "name": col,
                        "data": contents_to_appmap[col],
                        "yAxis": axis_idx,})
            axis_idx += 1
    #print "Categories"
    #print categories
    #print "Series"
    #print series
    return {
        "categories": categories,
        "series": series,
        "yaxis": yaxis,
        }


##################################################
###          Get raw file interfaces           ###
##################################################


def getpng(request, imgpath):
    """Return image response.
    
    Arguments:
    - `request`:
    - `imgpath`:
    """
    return getraw.getpng(request, imgpath)


def getstyle(request, stylefile):
    """Returns stylesheet file.

    @param request http request object
    @param stylefile stylesheet file path in the template directory
    """
    return getraw.getstyle(request, stylefile)


def getjs(request, path):
    """Returns javascript file.

    @param request http request object
    @param stylefile javascript file path in the template directory
    """
    return getraw.getjs(request, path)
