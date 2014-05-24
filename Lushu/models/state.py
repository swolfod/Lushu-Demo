__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models

class State(models.Model):
    name_en = models.CharField(max_length=64)
    name_cn = models.CharField(max_length=16)
    abbr = models.CharField()

    class Meta:
        db_table = "state"