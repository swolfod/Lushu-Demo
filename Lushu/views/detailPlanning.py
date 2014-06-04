__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from utilities.djangoUtils import *
from Lushu.models import *
from django.core.urlresolvers import reverse
from Lushu.utils import *
import math


def closestAirport(sight, international=True):
    city = getattr(sight, 'city', None)

    if city:
        airportQuery = Airport.objects.filter(city=city)
        if international:
            airportQuery = airportQuery.filter(international=True)

        airport = airportQuery.first()
        if airport:
            return airport

    airportQuery = Airport.objects
    if international:
        airportQuery = airportQuery.filter(international=True)
    airports = airportQuery.all()
    closest, distance = closestSight(sight.longitude, sight.latitude, [{"id": airport.id, "lng": airport.longitude, "lat": airport.latitude} for airport in airports])
    for airport in airports:
        if airport.id == closest["id"]:
            return airport
    else:
        raise Exception()


def getSight(sightKey):
    if "sights" not in getSight.__dict__:
        getSight.sights = {}

    if sightKey not in getSight.sights:
        if sightKey.startswith('tc'):
            getSight.sights[sightKey] = TravelCity.objects.get(pk=sightKey[2:])
        elif sightKey.startswith('mc'):
            getSight.sights[sightKey] = MajorCity.objects.get(pk=sightKey[2:])
        elif sightKey.startswith('pk'):
            getSight.sights[sightKey] = NationalPark.objects.get(pk=sightKey[2:])
        elif sightKey.startswith('ol'):
            getSight.sights[sightKey] = Outlet.objects.get(pk=sightKey[2:])
        elif sightKey.startswith('ap'):
            getSight.sights[sightKey] = Airport.objects.get(pk=sightKey[2:])

    return getSight.sights[sightKey]


def sightType(sightKey):
    if sightKey.startswith('tc'):
        return "city"
    elif sightKey.startswith('mc'):
        return "city"
    elif sightKey.startswith('pk'):
        return "nationalPark"
    elif sightKey.startswith('ol'):
        return "outlet"
    elif sightKey.startswith('ap'):
        return "airport"


def getCity(cityId):
    if "cities" not in getCity.__dict__:
        getCity.cities = {}

    if cityId not in getCity.cities:
        getCity.cities[cityId] = City.objects.get(pk=cityId)

    return getCity.cities[cityId]


def getNearCities(sightKey):
    sight = getSight(sightKey)
    sightCities = sight.nearCityInfo.order_by("distance").all()[:25]

    cityRanks = []
    for nearCity in sightCities:
        city = getCity(nearCity.city_id)
        bizInfo = city.bizInfo
        hotelCnt = bizInfo.hotelCnt if bizInfo else 0
        if hotelCnt < 1:
            hotelCnt = 1
        rank = math.sqrt(hotelCnt) / nearCity.distance
        cityRanks.append((city, rank, nearCity.distance))

    cityRanks.sort(key=lambda elem: elem[1], reverse=True)
    return [{"id": ele[0].id, "city": ele[0].name, "state": ele[0].state.abbr, "rank": ele[1], "distance": int(ele[2])} for ele in cityRanks]


def sightTitle(sight):
    return sight.name_en if "name_en" in sight.__dict__ else sight.name


def detailPlanning(request):
    sightsOrder = request.session.get("sightsOrder", None)
    sightsDistances = request.session.get("sightsDistances", None)
    durations = request.session.get("durations", None)

    if not sightsOrder or not sightsDistances or not durations:
        return HttpResponseRedirect(reverse("Lushu.views.datePlanning"))

    if request.method == "POST":
        planDetails = {}
        for key, value in request.POST.items():
            if key.startswith("planDay"):
                day = int(key[7:])
                planDetails[day] = json.loads(value)

        planDetails = [planDetails[key] for key in sorted(planDetails)]

        for dayPlan in planDetails:
            for step in dayPlan:
                if step["stepType"] == "way":
                    step["durationMin"] = int(step["duration"]) // 60

        request.session["planDetails"] = planDetails

        return HttpResponseRedirect(reverse("Lushu.views.getPlan"))

    durations = {k: float(v) for k,v in json.loads(durations).items()}
    visitSights = []
    for key in sightsOrder.split(","):
        key = key.strip()
        if key in durations and (durations[key] > 0 or key[:2] == "ap"):
            visitSights.append(key)

    plan = []
    nextDay = []
    currentDuration = 0
    for sightKey in visitSights:
        while currentDuration + durations[sightKey] > 1:
            if currentDuration < 1:
                nextDay.append((sightKey, 1 - currentDuration))
            plan.append(nextDay)

            nextDay = []
            durations[sightKey] -= 1 - currentDuration
            currentDuration = 0

        nextDay.append((sightKey, durations[sightKey]))
        currentDuration += durations[sightKey]

    if nextDay:
        plan.append(nextDay)

    sightCitiesDic = {}
    stays = []
    for i in range(len(plan) - 1):
        lastSightKey, lastDuration = plan[i][-1]
        nextSightKey, nextDuration = plan[i + 1][0]

        if lastSightKey in sightCitiesDic:
            lastSightCities = sightCitiesDic[lastSightKey]
        else:
            lastSightCities = getNearCities(lastSightKey)
            sightCitiesDic[lastSightKey] = lastSightCities

        if nextSightKey in sightCitiesDic:
            nextSightCities = sightCitiesDic[nextSightKey]
        else:
            nextSightCities = getNearCities(nextSightKey)
            sightCitiesDic[nextSightKey] = nextSightCities

        cityCandidates = {city["id"]: {
            "id": city["id"],
            "city": city["city"],
            "state": city["state"],
            "rank": city["rank"],
            "location": [{
                "sightKey": lastSightKey,
                "sightTitle": getSight(lastSightKey).title,
                "distance": city["distance"]
            }]
        } for city in lastSightCities}

        for city in nextSightCities:
            cityId = city["id"]
            if cityId in cityCandidates:
                if cityCandidates[cityId]["location"][0]["sightKey"] != nextSightKey:
                    cityCandidates[cityId]["location"].append({
                        "sightKey": nextSightKey,
                        "sightTitle": getSight(nextSightKey).title,
                        "distance": city["distance"]
                    })
            else:
                cityCandidates[cityId] = {
                    "id": city["id"],
                    "city": city["city"],
                    "state": city["state"],
                    "rank": city["rank"],
                    "location": [{
                        "sightKey": nextSightKey,
                        "sightTitle": getSight(nextSightKey).title,
                        "distance": city["distance"]
                    }]
                }

        recommendCity = cityCandidates[nextSightCities[0]["id"]]
        cityCandidates = [v for k, v in cityCandidates.items()]
        cityCandidates.sort(key=lambda city: city["rank"], reverse=True)

        stays.append({
            "candidates": cityCandidates,
            "recommend": recommendCity
        })

    detailPlan = []
    for day in plan:
        dayPlan = []
        for sightKey, duration in day:
            sight = getSight(sightKey)
            hourDuration = duration * 10

            planDetail = {
                "key": sightKey,
                "title": sight.title,
                "lng": sight.longitude,
                "lat": sight.latitude,
                "duration": hourDuration,
                "type": sightType(sightKey)
            }
            dayPlan.append(planDetail)

        detailPlan.append(dayPlan)

    return secureRender(request, "detailPlan.html", {
        "plan": detailPlan,
        "planJson": json.dumps(detailPlan, cls=DjangoJSONEncoder),
        "stays": stays,
        "staysJson": json.dumps(stays, cls=DjangoJSONEncoder),
        "lastPage": reverse("Lushu.views.datePlanning")
    })