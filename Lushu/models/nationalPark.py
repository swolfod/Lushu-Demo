__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models
from .city import City
from .state import State
from .hotel import Hotel
from .restaurant import Restaurant

class NationalPark(models.Model):
    name_en = models.CharField(max_length=128)
    name_cn = models.CharField(max_length=64, null=True)
    state = models.ForeignKey(State, null=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    area_acre = models.FloatField()
    area_km = models.FloatField()
    desc_en = models.TextField(null=True)
    desc_cn = models.TextField(null=True)
    established = models.DateField()
    wiki_en = models.CharField(max_length=256, null=True)
    wiki_cn = models.CharField(max_length=256, null=True)
    official_site = models.CharField(max_length=256, null=True)

    nearbyHotels = models.ManyToManyField(Hotel, db_table='park_hotel', related_name="nearbyNationalParks")
    nearbyRestaurants = models.ManyToManyField(Restaurant, db_table='park_restaurant', related_name="nearbyNationalParks")
    nearCities = models.ManyToManyField(City, through="ParkNearCity", related_name="nearParks")

    class Meta:
        db_table = "national_park"

    @property
    def title(self):
        return self.name_en


class ParkPhoto(models.Model):
    photoUrl = models.CharField(max_length=256)
    photoTitle = models.CharField(max_length=512, null=True)
    galleryTitle = models.CharField(max_length=512, null=True)
    toShow = models.BooleanField()

    park = models.ForeignKey(NationalPark, related_name="photos")

    class Meta:
        db_table = "park_photo"


class ParkNearCity(models.Model):
    park = models.ForeignKey(NationalPark, related_name="nearCityInfo")
    city = models.ForeignKey(City)
    distance = models.FloatField()

    class Meta:
        db_table = "park_nearbycity"