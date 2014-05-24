__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from django.core.urlresolvers import reverse
from Lushu.utils import *
from random import randint


def closestSight(lng, lat, sights):
    minDist = 9999999
    closest = None
    for sightKey, sight in sights.items():
        dist = calcDistance(lng, lat, sight["lng"], sight["lat"])
        if dist < minDist:
            minDist = dist
            closest = sight

    return closest, minDist


def datePlanning(request):
    sightJson = request.session.get("sights", None)
    if not sightJson:
        request.session["noSightsError"] = True
        return HttpResponseRedirect(reverse("Lushu.views.detailPlanning"))

    visitSights = json.loads(sightJson)
    noSightsError = False
    invalidDuration = False

    if request.method == "POST":
        sightsOrder = request.POST.get("order", None)
        sightsDistances = request.POST.get("distances", None)

        if sightsOrder:
            visitSights = [key.strip() for key in sightsOrder.split(",")]

            durations = {sightId: request.POST.get("duration-" + sightId) for sightId in visitSights}
            for key, value in durations.items():
                if not value or not isNumber(value):
                    invalidDuration = True
                    break
            else:
                request.session["sightsOrder"] = sightsOrder
                request.session["sightsDistances"] = sightsDistances
                request.session["sights"] = json.dumps(visitSights, cls=DjangoJSONEncoder)
                request.session["durations"] = json.dumps(durations, cls=DjangoJSONEncoder)

                return HttpResponseRedirect(reverse("Lushu.views.detailPlanning"))
        else:
            noSightsError = True
            planDic = json.loads(sightJson)

    destCityId = request.session.get("destCity", None)
    if not destCityId:
       return showHome()

    durationsJson = request.session.get("durations", None)
    durations = json.loads(durationsJson) if durationsJson else {}

    sightsOrder = request.session.get("sightsOrder", "")
    sightsDistances = request.session.get("sightsDistances", "")

    destCity = MajorCity.objects.get(pk=destCityId)
    sights = {}

    startSight = None

    for key in visitSights:
        sightInfo = {}
        if key.startswith('tc'):
            sight = TravelCity.objects.get(pk=key[2:])
            sightInfo["type"] = "city"
            sightInfo["title"] = sight.name
            sightInfo["duration"] = durations.get(key, randint(2, 4) / 2)

            if sight.city_id == destCity.city_id:
                startSight = sightInfo
        elif key.startswith('pk'):
            sight = NationalPark.objects.get(pk=key[2:])
            sightInfo["type"] = "nationalPark"
            sightInfo["title"] = sight.name_en
            sightInfo["duration"] = durations.get(key, randint(2, 4) / 2)
        elif key.startswith('ol'):
            sight = Outlet.objects.get(pk=key[2:])
            sightInfo["type"] = "outlet"
            sightInfo["title"] = sight.name
            sightInfo["duration"] = durations.get(key, 0.5)
        else:
            continue

        sightInfo["key"] = key
        sightInfo["lng"] = sight.longitude
        sightInfo["lat"] = sight.latitude

        if sightInfo != startSight:
            sights[key] = sightInfo

    if not startSight:
        destKey = "mc" + str(destCityId)
        startSight = {
            "key": destKey,
            "title": destCity.name_en,
            "lng": destCity.longitude,
            "lat": destCity.latitude,
            "duration": randint(2, 4) / 2 if destKey in planDic else 0,
            "type": "city"
        }

    if sightsOrder:
        try:
            sights[startSight["key"]] = startSight
            sightPlan = [sights[key.strip()] for key in sightsOrder.split(",")]
        except:
            return showHome()
    else:
        sightPlan = [startSight]
        sightsOrder = startSight["key"]

        while len(sights) > 0:
            nextSight, dist = closestSight(startSight["lng"], startSight["lat"], sights)
            sightPlan.append(nextSight)
            sights.pop(nextSight["key"], None)
            sightsOrder += ", " + nextSight["key"]
            startSight = nextSight

    return secureRender(request, "datePlan.html", {
        "sights": sightPlan,
        "sightsJson": json.dumps(sightPlan, cls=DjangoJSONEncoder),
        "noSightsError": noSightsError,
        "invalidDuration": invalidDuration,
        "sightsOrder": sightsOrder,
        "sightsDistances": sightsDistances,
        "lastPage": reverse("Lushu.views.selSights")
    })