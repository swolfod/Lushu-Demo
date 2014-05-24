__author__ = 'Swolfod'
# -*- coding: utf-8 -*-

from django.db import models
from .state import State

class City(models.Model):
    name = models.CharField(max_length=128)
    state = models.ForeignKey(State, null=True)

    class Meta:
        db_table = "city"