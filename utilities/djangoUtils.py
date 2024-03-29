__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.core.context_processors import csrf
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, render_to_response
from django.contrib.auth.models import User
from io import FileIO, BufferedWriter
from uuid import uuid1
import os
from PIL import Image
from io import BytesIO, StringIO
import json
import decimal
from django.views.generic import TemplateView
from django.template import RequestContext
from datetime import datetime, timedelta
from django.http import *
from django.core.serializers.json import DjangoJSONEncoder
from math import sin, cos, sqrt, atan2, radians


def getOrNone(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def secureRender(request, template, dic, userContext=True):
    dic.update(csrf(request))
    if userContext:
        return render_to_response(template, dic, context_instance=RequestContext(request))
    else:
        return render_to_response(template, dic)

def respondJson(context, success=True):
    return HttpResponse(json.dumps({"success": True if success else False, "result": context}, cls=DjangoJSONEncoder))


def getCurrentUser(request):
    if request.user.is_authenticated():
        return request.user

    return None


def randomImageName(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid1().hex, ext)
    return os.path.join("images", filename)


def save_upload(uploaded, filename, raw_data ):
    """
    raw_data: if True, uploaded is an HttpRequest object with the file being
              the raw post data
              if False, uploaded has been submitted via the basic form
              submission and is a regular Django UploadedFile in request.FILES
    """
    try:
        with BufferedWriter( FileIO( filename, "wb" ) ) as dest:
            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                foo = uploaded.read( 1024 )
                while foo:
                    dest.write( foo )
                    foo = uploaded.read( 1024 )
                    # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                for c in uploaded.chunks():
                    dest.write(c)
                # got through saving the upload, report success
            return True
    except IOError:
        # could not open the file most likely
        pass
    return False


def saveUploadedImage(uploaded, raw_data, mediaRoot):
    """
    raw_data: if True, uploaded is an HttpRequest object with the file being
              the raw post data
              if False, uploaded has been submitted via the basic form
              submission and is a regular Django UploadedFile in request.FILES
    """
    try:
        # if the "advanced" upload, read directly from the HTTP request
        # with the Django 1.3 functionality
        if raw_data:
            foo = uploaded.read(1024)
            fileContent = foo
            while foo:
                foo = uploaded.read(1024)
                fileContent += foo
                # if not raw, it was a form upload so read in the normal Django chunks fashion

            image = Image.open(BytesIO(fileContent))
        else:
            fileContent = bytearray()
            for c in uploaded.chunks():
                fileContent += c
                # got through saving the upload, report success

            image = Image.open(BytesIO(fileContent))

        # if not RGB, convert
        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")

        fileName = randomImageName(None, "a.jpg")
        image.save(os.path.join(mediaRoot, fileName).replace("\\", "/"), "JPEG")

        return fileName
    except IOError:
        # could not open the file most likely
        pass
    return None


class AnonymousRequired(object):
    def __init__(self, view_function, redirect_to):
        if redirect_to is None:
            from django.conf import settings
            redirect_to = settings.LOGIN_REDIRECT_URL
        self.view_function = view_function
        self.redirect_to = redirect_to

    def __call__(self, request, *args, **kwargs):
        if request.user is not None and request.user.is_authenticated():
            return HttpResponseRedirect(self.redirect_to)
        return self.view_function(request, *args, **kwargs)


def anonymous_required(view_function, redirect_to=None):
    return AnonymousRequired(view_function, redirect_to)


def addParameter(url, parName, parVar):
    prefix = "?" if "?" not in url else "&"
    return url + prefix + parName + "=" + parVar


class DirectTemplateView(TemplateView):
    extra_context = None
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in self.extra_context.items():
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context


class DefaultJSONEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DefaultJSONEncoder, self)._iterencode(o, markers)


class ForceDefaultLanguageMiddleware(object):
    """
    Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies

    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    namely django.middleware.locale.LocaleMiddleware
    """
    def process_request(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']


class NoCacheMiddleware(object):

    def process_response(self, request, response):

        response['Pragma'] = 'no-cache'
        response['Cache-Control'] = 'max-age=3600 must-revalidate proxy-revalidate'
        response['Expires'] = '0'

        return response


def SmartTruncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix


def pageItems(query, page, itemPerPage):
    page = int(page)
    if page < 1:
        page = 1

    startNum = (page - 1) * itemPerPage
    endNum = startNum + itemPerPage + 1

    items = query.all()[startNum:endNum]

    if not items and page > 1:
        count = query.count()
        page = (count - 1) // itemPerPage + 1
        startNum = (page - 1) * itemPerPage
        endNum = startNum + itemPerPage + 1
        items = query.all()[startNum:endNum]

    previousPage = page - 1
    nextPage = page + 1 if len(items) > itemPerPage else 0
    if items:
        items = items[:len(items) - 1]

    return items, previousPage, nextPage


def delta2dict( delta ):
    """Accepts a delta, returns a dictionary of units"""
    delta = abs( delta )
    return {
        'year'   : int(delta.days / 365),
        'month'  : int(delta.days / 30),
        'day'    : int(delta.days % 365),
        'hour'   : int(delta.seconds / 3600),
        'minute' : int(delta.seconds / 60) % 60,
        'second' : delta.seconds % 60,
        'microsecond' : delta.microseconds
    }


def human(dt, precision=1, past_tense='{} ago', future_tense='in {}'):
    """Accept a datetime or timedelta, return a human readable delta string"""
    delta = dt
    if type(dt) is not type(timedelta()):
        delta = datetime.now() - dt

    the_tense = past_tense
    if delta < timedelta(0):
        the_tense = future_tense

    d = delta2dict( delta )
    hlist = []
    count = 0
    units = ( 'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond' )
    for unit in units:
        if count >= precision: break # met precision
        if d[ unit ] == 0: continue # skip 0's
        s = '' if d[ unit ] == 1 else 's' # handle plurals
        hlist.append( '%s %s%s' % ( d[unit], unit, s ) )
        count += 1
    human_delta = ', '.join( hlist )
    return the_tense.format(human_delta)


def calcDistance(lng1, lat1, lng2, lat2):
    lng1 = radians(lng1)
    lat1 = radians(lat1)
    lng2 = radians(lng2)
    lat2 = radians(lat2)

    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return 6373.0 * c


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False
