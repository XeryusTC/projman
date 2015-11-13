# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement

class BaseProjectPage(PageObject):
    logout  = PageElement(link_text='LOG OUT')
    sidebar = PageElement(id_="sidedrawer")
    sidebar_hide = PageElement(class_name='.js-hide-sidebar')
    sidebar_show = PageElement(class_name='.js-show-sidebar')
