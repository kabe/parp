# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
import resource
import math
import time

import sys
path = "/home/kabe/git/prof/tau/"
if path not in sys.path:
    sys.path.append(path)

#import tau
import util
import db
import nm.loader
import TauLoad.Loader


def helloworld(request):
    return HttpResponse("Hello World")


def usetemplate(request):
    return render_to_response('ut.html',
                              {"hensu1": "HENSU1",
                               "hensu2": "HENSU2"})


def pgroupdiff(request, pg1, pg2):
    """

    @param request
    @param pg1
    @param pg2
    """
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    time1 = time.time()
    conn = db.init("sqlite3", dbfile="/home/kabe/Archives/prof.db")
    #conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
    # Params
    stranger_diffpercent_thresh = 1.0
    params = {"stranger_diffpercent_thresh": stranger_diffpercent_thresh,
              "stranger_diffpercent_thresh_neg": -stranger_diffpercent_thresh,
              }
    # Main comparation
    sql = """
SELECT pr1.funcname,
       pr1.ratio R1,
       pr2.ratio R2,
       (pr2.ratio - pr1.ratio) * 100 AS ratiodiff
FROM (SELECT * FROM pgroup_ratio WHERE profgroup_id = ?) pr1,
     (SELECT * FROM pgroup_ratio WHERE profgroup_id = ?) pr2
WHERE pr1.funcname = pr2.funcname
ORDER BY ABS(pr2.ratio - pr1.ratio) DESC
;
"""
    r_main = ()
    if pg1 != pg2:
        r_main = conn.select(sql, (pg1, pg2))
    # New comparison
    newc_colnames = ("PG L", "PG R",
                     "Application", "Place", "# of nodes",
                     "# of Processes", "Library", "Avg. Time", "StdDev.")
    newc = """
SELECT profgroup.id,
       application,
       place,
       nodes,
       profgroup.procs,
       library,
       avg_time,
       var
FROM profgroup,
     pgroup_meta
WHERE profgroup.id = pgroup_meta.profgroup_id
ORDER BY profgroup.id
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
                              {"params": params,
                               "pg1": int(pg1),
                               "pg2": int(pg2),
                               "result": r_main,
                               "rnc_n": newc_colnames,
                               "rnc": r_newc2,
                               "rd": rd})

