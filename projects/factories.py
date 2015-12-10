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

    text = factory.Sequence(lambda n: 'Action %d' % n)


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = 'projects.Project'

    name = factory.Sequence(lambda n: 'Project %d' % n)
