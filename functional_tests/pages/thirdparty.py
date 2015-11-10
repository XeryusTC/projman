# -*- coding:utf-8 -*-
from page_objects import PageObject, PageElement

class Persona(PageObject):
    email = PageElement(id_='authentication_email')
