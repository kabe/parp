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
import cPickle

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
import memcachedwrapper


def getpng(request, imgpath):
    """Return png image response.
    
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
    return response


def getstyle(request, stylefile):
    """Returns stylesheet file.

    @param request http request object
    @param stylefile stylesheet file path in the template directory
    """
    try:
        with open(os.path.join("viewer", "templates", stylefile)) as f:
            data = f.read()
    except:
        raise Http404
    response = HttpResponse(data, mimetype='text/css')
    return response


def getjs(request, path):
    """Returns javascript file.

    @param request http request object
    @param stylefile javascript file path in the template directory
    """
    try:
        with open(os.path.join("viewer", "templates", path)) as f:
            data = f.read()
    except:
        raise Http404
    response = HttpResponse(data, mimetype='text/javascript')
    return response
