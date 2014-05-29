__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models
from .state import State
from .city import City

class Airport(models.Model):
    name_en = models.CharField(max_length=128)
    name_cn = models.CharField(max_length=64, null=True)
    faa = models.CharField()
    iata = models.CharField()
    icao = models.CharField()
    desc_en = models.TextField(null=True)
    desc_cn = models.TextField(null=True)
    city = models.ForeignKey(City)
    state = models.ForeignKey(State)
    longitude = models.FloatField()
    latitude = models.FloatField()
    international = models.BooleanField()

    @property
    def title(self):
        return self.name_en

    class Meta:
        db_table = "airport"