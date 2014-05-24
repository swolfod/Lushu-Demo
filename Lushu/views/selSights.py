__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from Lushu.consts import *
from operator import attrgetter
from random import randint
from django.core.urlresolvers import reverse
import json
from django.core.serializers.json import DjangoJSONEncoder

def selSights(request):
    if request.method == "POST":
        planDic = {}
        planDic.update(request.POST)
        planDic.pop("csrfmiddlewaretoken", None)
        visitSights = [sightKey for sightKey in planDic]
        request.session["sights"] = json.dumps(visitSights, cls=DjangoJSONEncoder)
        request.session.pop("sightsOrder", None)
        request.session.pop("sightsDistances", None)
        request.session.pop("durations", None)
        return HttpResponseRedirect(reverse("Lushu.views.datePlanning"))

    noSightsError = request.session.get("noSightsError", False)
    request.session.pop("noSightsError", None)

    planDic = {}
    if request.session.get("sights", None):
        planDic = json.loads(request.session.get("sights"))

    destCityId = request.GET.get("destination")
    if not destCityId:
        majorCities = [city for city in MajorCity.objects.order_by("id")[:50]]
        majorCities.sort(key = attrgetter('name_en'))

        return secureRender(request, "home.html", {"majorCities": majorCities, "invalid": {"destination": True}})
    else:
        destination = MajorCity.objects.get(pk=destCityId)
        request.session["destCity"] = destCityId

        startLat = destination.latitude
        startLng = destination.longitude

        travelCities = TravelCity.objects.filter(longitude__gte=startLng - 6, longitude__lte=startLng + 6, latitude__gte=startLat - 4, latitude__lte=startLat + 4).all()
        citySights = []
        foundTravel = False
        for travelCity in travelCities:
            sightId = "tc" + str(travelCity.id)
            if travelCity.city_id == destination.city_id:
                citySights.insert(0, {
                    "id": sightId,
                    "title": travelCity.name,
                    "pic": travelCity.imgUrl,
                    "rating": randint(1, 10) / 2,
                    "toVisit": sightId in planDic,
                    "minDuration": randint(1, 2) / 2,
                    "maxDuration": randint(2, 6) / 2
                })

                foundTravel = True
            else:
                citySights.append({
                    "id": sightId,
                    "title": travelCity.name,
                    "pic": travelCity.imgUrl,
                    "rating": randint(1, 10) / 2,
                    "toVisit": sightId in planDic,
                    "minDuration": randint(1, 2) / 2,
                    "maxDuration": randint(2, 6) / 2
                })

        if not foundTravel:
            sightId = "mc" + str(destination.id)
            citySights.insert(0, {
                "id": sightId,
                "title": destination.name_en,
                "pic": destination.imgUrl,
                "rating": randint(1, 10) / 2,
                "toVisit": sightId in planDic,
                "minDuration": randint(1, 2) / 2,
                "maxDuration": randint(2, 6) / 2
            })

        nationalParks = NationalPark.objects.filter(longitude__gte=startLng - 6, longitude__lte=startLng + 6, latitude__gte=startLat - 4, latitude__lte=startLat + 4).all()

        parkSights = []
        for park in nationalParks:
            sightId = "pk" + str(park.id)
            parkSights.append({
                "id": sightId,
                "title": park.name_en,
                "pic": reverse("images.views.getImage", args=(park.photos.filter(toShow=True).first().photoUrl, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)),
                "rating": randint(1, 10) / 2,
                "toVisit": sightId in planDic,
                "minDuration": randint(1, 2) / 2,
                "maxDuration": randint(2, 6) / 2
            })


        outlets = Outlet.objects.filter(longitude__gte=startLng - 6, longitude__lte=startLng + 6, latitude__gte=startLat - 4, latitude__lte=startLat + 4).all()
        outletSights = []
        for outlet in outlets:
            sightId = "ol" + str(outlet.id)

            outletSights.append({
                "id": sightId,
                "title": outlet.name,
                "pic": "http://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom=8&size={2}x{3}&maptype=roadmap&markers=color:red%7C{0},{1}&sensor=false".format(outlet.latitude, outlet.longitude, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT),
                "rating": randint(1, 10) / 2,
                "toVisit": sightId in planDic,
                "minDuration": 0.5,
                "maxDuration": 0.5
            })

        return secureRender(request, "selSights.html", {
            "citySights": citySights,
            "parkSights": parkSights,
            "outletSights": outletSights,
            "noSightsError": noSightsError,
            "lastPage": reverse("Lushu.views.homePage")
        })