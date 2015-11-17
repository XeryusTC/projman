# -*- coding: utf-8 -*-
from factory.django import DjangoModelFactory

class InlistItemFactory(DjangoModelFactory):
    class Meta:
        model = 'projects.InlistItem'
