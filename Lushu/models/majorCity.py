__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models
from .city import City
from .state import State

class MajorCity(models.Model):
    name_en = models.CharField(max_length=32)
    name_cn = models.CharField(max_length=32, null=True)
    city = models.ForeignKey(City, null=True)
    state = models.ForeignKey(State)
    desc_en = models.TextField()
    desc_cn = models.TextField(null=True)
    imgUrl = models.CharField(max_length=512, null=True)
    rank = models.IntegerField()
    wikiUrl_en = models.CharField(max_length=256)
    wikiUrl_cn = models.CharField(max_length=256, null=True)
    lngW = models.FloatField()
    lngE = models.FloatField()
    latN = models.FloatField()
    latS = models.FloatField()
    longitude = models.FloatField()
    latitude = models.FloatField()

    class Meta:
        db_table = "major_city"