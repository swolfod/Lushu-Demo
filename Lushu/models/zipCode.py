__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models
from .state import State
from .city import City

class ZipCode(models.Model):
    zip = models.CharField()
    city = models.ForeignKey(City)
    state = models.ForeignKey(State)
    longitude = models.FloatField()
    latitude = models.FloatField()

    class Meta:
        db_table = "zipcode"