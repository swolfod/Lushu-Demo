__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from django.core.urlresolvers import reverse
from Lushu.utils import *
from random import randint


def datePlanning(request):
    destArea = request.session.get("destArea", None)
    if not destArea:
        return secureRender(request, "home.html", {"areas": Areas, "invalid": {"destination": True}})

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

            durations = {sightId: request.POST.get("duration-" + sightId) if sightId[:2] != "ap" else 0 for sightId in visitSights}
            for key, value in durations.items():
                if not isNumber(value):
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

    sightsOrder = request.session.get("sightsOrder", None)
    durationsJson = request.session.get("durations", None)
    durations = json.loads(durationsJson) if durationsJson else {}

    sights = []

    for key in visitSights:
        sightInfo = {}
        if key.startswith('tc'):
            sight = TravelCity.objects.get(pk=key[2:])
            sightInfo["type"] = "city"
            sightInfo["title"] = sight.name
            sightInfo["duration"] = durations.get(key, randint(2, 4) / 2)
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

        sights.append(sightInfo)

    allAirports = Airport.objects.filter(international=True, longitude__gte=destArea["lngW"], longitude__lte=destArea["lngE"], latitude__gte=destArea["latS"], latitude__lte=destArea["latN"]).all()
    airportSights = {}
    for sight in sights:
        airportDist = []
        for airport in allAirports:
            distance = calcDistance(sight["lng"], sight["lat"], airport.longitude, airport.latitude)
            airportDist.append((airport.id, distance))

        airportDist.sort(key = lambda ele: ele[1])
        closestAirportId, closestDist = airportDist[0]
        sight["airports"] = [{"airportId": closestAirportId, "distance": closestDist}]
        if closestAirportId not in airportSights:
            airportSights[closestAirportId] = []
        airportSights[closestAirportId].append({"sightKey": sight["key"], "sightTitle": sight["title"], "distance": int(closestDist)})
        for i in range(1, len(airportDist)):
            airportId, distance = airportDist[i]
            if distance > closestDist + 100:
                break

            sight["airports"].append({"airportId": airportId, "distance": distance})
            if airportId not in airportSights:
                airportSights[airportId] = []
            airportSights[airportId].append({"sightKey": sight["key"], "sightTitle": sight["title"], "distance": int(distance)})

    airportDic = {airport.id: airport for airport in allAirports}
    airports = []
    for airportId, closeSights in airportSights.items():
        closeSights.sort(key = lambda ele: ele["distance"])
        airport = airportDic[airportId]

        airportInfo = {
            "id": airportId,
            "title": airport.title,
            "lat": airport.latitude,
            "lng": airport.longitude,
            "sights": [closeSights[0]]
        }

        for i in range(1, len(closeSights)):
            if closeSights[i]["distance"] > closeSights[0]["distance"] + 50 or i > 2:
                break
            airportInfo["sights"].append(closeSights[i])

        airports.append(airportInfo)

    tripDuration = request.session.get("tripDuration", 0)
    return secureRender(request, "datePlan.html", {
        "sights": sights,
        "sightsJson": json.dumps(sights, cls=DjangoJSONEncoder),
        "airports": airports,
        "airportsJson": json.dumps(airports, cls=DjangoJSONEncoder),
        "noSightsError": noSightsError,
        "invalidDuration": invalidDuration,
        "tripDuration": tripDuration,
        "sightsOrder": sightsOrder if sightsOrder else "",
        "lastPage": reverse("Lushu.views.selSights")
    })