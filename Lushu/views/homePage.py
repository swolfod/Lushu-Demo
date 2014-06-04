__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from operator import attrgetter
from Lushu.consts import *

def homePage(request):
    return secureRender(request, "home.html", {"areas": Areas})