# Create your views here.
from django.http import HttpResponse
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

import sys
import os
import os.path
path = os.path.join(os.environ["HOME"], "git/prof/tau/")
if path not in sys.path:
    sys.path.append(path)

import util
import db
import nm.loader
import TauLoad.Loader


def helloworld(request):
    #return HttpResponse("Hello World")
    return HttpResponseRedirect("/pgdiff/1/1/")


def pgd1_dummy(request):
    """redirector
    
    Arguments:
    - `request`:
    """
    return HttpResponseRedirect("/pgd1/ratiodiff/desc/ratio/1/7/")


def usetemplate(request):
    return render_to_response('ut.html',
                              {"hensu1": "HENSU1",
                               "hensu2": "HENSU2"})

@cache_page(60 * 5)
def pgroupdiff(request, pg1, pg2):
    """Show ProfGroup difference.

    @param request
    @param pg1
    @param pg2
    """
    view_meter_diffratio_max = 10
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    time1 = time.time()
    params = ViewParam.objects.get()
    dbtype = params.dbtype
    if dbtype == "sqlite3":
        conn = db.init("sqlite3", dbfile=params.sqlite3_file)
    elif dbtype == "postgres":
        conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
    else:
        raise Http404
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
    """
    
    Arguments:
    - `request`:
    - `params`:
    """
    print params
    return HttpResponseRedirect(reverse('parpview.viewer.pgdiff'), args=(1, 1))


def pgview(request, pg_id):
    """Detail view of ProfGroup.

    Arguments:
    - `request`:
    - `pg_id`:
    """
    # Log
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    time1 = time.time()
    # Params
    params = ViewParam.objects.get()
    dbtype = params.dbtype
    if dbtype == "sqlite3":
        conn = db.init("sqlite3", dbfile=params.sqlite3_file)
    elif dbtype == "postgres":
        conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
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


def getimage(request, imgpath):
    """Return image response.
    
    Arguments:
    - `request`:
    - `imgpath`:
    """
    with open(os.path.join("viewer", "data", imgpath)) as f:
        try:
            img_data = f.read()
        except:
            raise Http404
        response = HttpResponse(img_data, mimetype='image/png')
    
    #response['Content-Disposition'] = 'attachment; filename=foo.xls'
    return response


@cache_page(60 * 30)
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
        conn = db.init("sqlite3", dbfile=params.sqlite3_file)
    elif dbtype == "postgres":
        conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
    else:
        raise Http404
    # Param
    stranger_diff_thresh = params.susp_thresh
    t_params = {"stranger_diffpercent_thresh": stranger_diff_thresh * 100,
                "stranger_diffpercent_thresh_neg": -stranger_diff_thresh * 100,
                "susp_ratio_thresh": params.susp_ratio_thresh * 100,
                "vmdfrmax": view_meter_diffratio_max,
                }
    # Sort order
    print "order:" + order
    if order == "timediff":
        order_str = "ABS(pr1.excl_pe_rank_avg - pr2.excl_pe_rank_avg)"
    elif order == "speedup":
        order_str = "ABS(pr1.excl_pe_rank_avg / pr2.excl_pe_rank_avg)"
    elif order == "ratiodiff":
        order_str = "ABS(pr1.ratio - pr2.ratio)"
    else:
        raise Http404
    # Sort mode
    print "sortmode:" + sortmode
    if sortmode == "asc":
        order_str += " ASC"
    elif sortmode == "desc":
        order_str += " DESC"
    else:
        raise Http404
    # Main comparation
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
        r_main = conn.select(sql_str, (pg1, pg2))
        r1_max, r2_max = max(x[2] for x in r_main), max(x[4] for x in r_main)
#     # New comparison
#     newc_colnames = ("PG L", "PG R",
#                      "Application", "Place", "# of nodes",
#                      "# of Processes", "Library", "Avg. Time", "StdDev.",
#                      "PG L2", "PG R2")
#     newc = """
# SELECT pg.id,
#        pg.application,
#        pg.place,
#        pg.nodes,
#        pg.procs,
#        pg.library,
#        pgm.avg_time,
#        pgm.var
# FROM profgroup AS pg,
#      pgroup_meta AS pgm
# WHERE pg.id = pgm.profgroup_id
# ORDER BY pg.id
# ;
# """
#     r_newc = conn.select(newc)
#     # stddev
#     r_newc2 = (r[0:-1] + (math.sqrt(r[-1]),) for r in r_newc)
#     #print r_newc2
    # Log
    ru2 = resource.getrusage(resource.RUSAGE_SELF)
    time2 = time.time()
    rd = (ru2.ru_utime - ru1.ru_utime,
          ru2.ru_stime - ru1.ru_stime,
          ru2.ru_inblock - ru1.ru_inblock,
          ru2.ru_oublock - ru1.ru_oublock,
          time2 - time1,
          )
    print rd
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


def gengraph(index_A, index_B, mode, funcs):
    """Generate GNUPLOT Graph.
    
    @param index_A index for A
    @param index_B index for B
    @param mode "exectime" or "ratio"
    @param funcs
    """
    plot_template = """reset
set terminal postscript eps color "Gothic-BBB-EUC-H" 96
set size 4
set title "${title}"
set output "out.eps"
set grid
set key above
${xtics_conf}
set xtics rotate
plot "${datafile}" using ($1-2):${col_A}:(4) title "A" w boxes fs solid 1, \
     "${datafile}" using ($1+2):${col_B}:(4) title "B" w boxes fs solid 1
"""
    template = string.Template(plot_template)
    # Determine image file name
    cur_time = time.time()
    image_filename = str(cur_time) + ".png"
    # xtics
    xtics_t = """set xtics(${conf})"""
    xtics_tt = string.Template(xtics_t)
    xtics_list = []
    if mode == "exectime":
        title = "Execution Time"
        col_A = 2
        col_B = 3
    elif mode == "ratio":
        title = "Ratio"
        col_A = 5
        col_B = 6
    else:
        raise Http404
    label_A = str(index_A)
    label_B = str(index_B)
    timedata = ""
    line_t = "${index} ${t1} ${t2} ${ratio} ${r1} ${r2} ${rdiff}" + "\n"
    tt = string.Template(line_t)
    for i, t in enumerate(funcs):
        #print i, t
        if i >= 10: break
        ts = tt.safe_substitute(index=i * 10,
                                t1=t[2], t2=t[4], ratio=t[5],
                                r1=t[1], r2=t[3], rdiff=t[6])
        timedata += ts
        xtics_list.append('"' + t[0][:-2] + '"' + " " + str(i * 10))
    tmpfilename = os.tmpnam()
    xtics_conf = xtics_tt.substitute(conf=",".join(xtics_list))
    s = template.safe_substitute(title=title,
                                 datafile=tmpfilename,
                                 xtics_conf=xtics_conf,
                                 col_A=col_A,
                                 col_B=col_B)
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
    os.unlink(tmpfilename)
    print "DONE"
    return image_filename
