__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from django.core.urlresolvers import reverse
from Lushu.utils import *
from random import randint


def detailPlanning(request):

    return secureRender(request, "detailPlan.html", {})