__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from operator import attrgetter
from random import randint
from django.core.urlresolvers import reverse
from Lushu.consts import *

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


def sightsInArea(latN, latS, lngE, lngW):
    cities = {}
    travelCities = TravelCity.objects.filter(longitude__gte=lngW, longitude__lte=lngE, latitude__gte=latS, latitude__lte=latN).all()
    for travelCity in travelCities:
        sightId = "tc" + str(travelCity.id)
        cities[travelCity.city_id] = {
            "id": sightId,
            "title": travelCity.name,
            "pic": travelCity.imgUrl,
            "rating": randint(1, 10) / 2,
            "lat": travelCity.latitude,
            "lng": travelCity.longitude,
            "minDuration": randint(1, 2) / 2,
            "maxDuration": randint(2, 6) / 2
        }

    majorCities = MajorCity.objects.filter(id__lte=50, longitude__gte=lngW, longitude__lte=lngE, latitude__gte=latS, latitude__lte=latN).all()
    for majorCity in majorCities:
        if majorCity.city_id in cities:
            continue

        sightId = "mc" + str(travelCity.id)
        cities[travelCity.city_id] = {
            "id": sightId,
            "title": majorCity.name_en,
            "pic": majorCity.imgUrl,
            "rating": randint(1, 10) / 2,
            "lat": majorCity.latitude,
            "lng": majorCity.longitude,
            "minDuration": randint(1, 2) / 2,
            "maxDuration": randint(2, 6) / 2
        }

    citySights = [sight for cityId, sight in cities.items()]

    nationalParks = NationalPark.objects.filter(longitude__gte=lngW, longitude__lte=lngE, latitude__gte=latS, latitude__lte=latN).all()
    parkSights = []
    for park in nationalParks:
        sightId = "pk" + str(park.id)
        parkSights.append({
            "id": sightId,
            "title": park.name_en,
            "pic": reverse("images.views.getImage", args=(park.photos.filter(toShow=True).first().photoUrl, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)),
            "rating": randint(1, 10) / 2,
            "lat": park.latitude,
            "lng": park.longitude,
            "minDuration": randint(1, 2) / 2,
            "maxDuration": randint(2, 6) / 2
        })


    outlets = Outlet.objects.filter(longitude__gte=lngW, longitude__lte=lngE, latitude__gte=latS, latitude__lte=latN).all()
    outletSights = []
    for outlet in outlets:
        sightId = "ol" + str(outlet.id)

        outletSights.append({
            "id": sightId,
            "title": outlet.name,
            "pic": "http://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom=8&size={2}x{3}&maptype=roadmap&markers=color:red%7C{0},{1}&sensor=false".format(outlet.latitude, outlet.longitude, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT),
            "rating": randint(1, 10) / 2,
            "lat": outlet.latitude,
            "lng": outlet.longitude,
            "minDuration": 0.5,
            "maxDuration": 0.5
        })

    return citySights, parkSights, outletSights