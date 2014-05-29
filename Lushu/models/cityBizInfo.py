__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models
from .city import City
from .state import State

class CityBizInfo(models.Model):
    city = models.OneToOneField(City, related_name="bizInfo")
    restaurantCnt = models.IntegerField()
    restaurantPrice = models.FloatField()
    restaurantRate = models.FloatField()
    hotelCnt = models.IntegerField()
    hotelPrice = models.FloatField()
    hotelRate = models.FloatField()

    class Meta:
        db_table = "city_biz"