__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=256)
    rating = models.FloatField()
    reviewCnt = models.IntegerField()
    priceRange = models.CharField(null=True)
    streetAddress = models.CharField(null=True)
    cityAddress = models.CharField(null=True)
    imgUrl = models.CharField(null=True)
    phone = models.CharField(null=True)
    yelpId = models.CharField(max_length=64)
    yelpUrl = models.CharField(max_length=256)
    longitude = models.FloatField()
    latitude = models.FloatField()

    class Meta:
        db_table = "restaurant"