__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models

class BrandStore(models.Model):
    brandName = models.CharField(max_length=128)

    class Meta:
        db_table = "brand_store"