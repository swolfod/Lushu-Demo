__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from operator import attrgetter

def showHome():
    majorCities = [city for city in MajorCity.objects.order_by("id")[:50]]
    majorCities.sort(key = attrgetter('name_en'))

    return secureRender(request, "home.html", {"majorCities": majorCities, "invalid": {"destination": True}})


def closestSight(lng, lat, sights):
    minDist = 9999999
    closest = None
    for sight in sights:
        dist = calcDistance(lng, lat, sight["lng"], sight["lat"])
        if dist < minDist:
            minDist = dist
            closest = sight

    return closest, minDist