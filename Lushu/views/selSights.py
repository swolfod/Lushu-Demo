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
from Lushu.utils import *

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
        planDic = {sightKey:True for sightKey in json.loads(request.session.get("sights"))}

    destArea = request.GET.get("destination")
    if not destArea:
        destination = request.session.get("destArea", None)
    else:
        destination = Areas[int(destArea)]

    try:
        tripDuration = int(request.GET.get("duration"))
        request.session["tripDuration"] = tripDuration
    except:
        request.session.pop("tripDuration", None)

    if not destination:
        return secureRender(request, "home.html", {"areas": Areas, "invalid": {"destination": True}})
    else:
        request.session["destArea"] = destination

        citySights, parkSights, outletSights = sightsInArea(destination["latN"], destination["latS"], destination["lngE"], destination["lngW"])

        return secureRender(request, "selSights.html", {
            "citySights": citySights,
            "parkSights": parkSights,
            "outletSights": outletSights,
            "visiting": planDic,
            "noSightsError": noSightsError,
            "lastPage": reverse("Lushu.views.homePage")
        })