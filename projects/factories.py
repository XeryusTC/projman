# -*- coding: utf-8 -*-
import factory
from factory.django import DjangoModelFactory

class InlistItemFactory(DjangoModelFactory):
    class Meta:
        model = 'projects.InlistItem'

    text = factory.Sequence(lambda n: 'Inlist item %d' %n)


class ActionlistItemFactory(DjangoModelFactory):
    class Meta:
        model = 'projects.ActionlistItem'
