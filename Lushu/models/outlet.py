__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models
from .state import State
from .brandStore import BrandStore

class Outlet(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=512, null=True)
    state = models.ForeignKey(State, null=True)
    storeNum = models.IntegerField()
    phoneNum = models.CharField(max_length=128, null=True)
    desc = models.TextField(null=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    openingHours = models.TextField(null=True)

    stores = models.ManyToManyField(BrandStore, db_table='outlet_store', related_name="outlets")

    class Meta:
        db_table = "outlet"