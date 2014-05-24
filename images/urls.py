__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns("images.views",
                       (r"^getImage/(\w+)/(\d+)/(\d+)/$", "getImage"),
                       )