__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models
from .city import City
from .state import State

class TravelCity(models.Model):
    name = models.CharField(max_length=64)
    city = models.ForeignKey(City)
    state = models.ForeignKey(State)
    desc = models.TextField()
    imgUrl = models.CharField(max_length=256, null=True)
    rank = models.IntegerField()
    lngW = models.FloatField()
    lngE = models.FloatField()
    latN = models.FloatField()
    latS = models.FloatField()
    longitude = models.FloatField()
    latitude = models.FloatField()

    nearCities = models.ManyToManyField(City, through="TravelNearCity", related_name="nearTravelCities")

    class Meta:
        db_table = "travel_city"

    @property
    def title(self):
        return self.name


class TravelNearCity(models.Model):
    travelCity = models.ForeignKey(TravelCity, related_name="nearCityInfo")
    city = models.ForeignKey(City)
    distance = models.FloatField()

    class Meta:
        db_table = "travelcity_nearbycity"