# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement

class BaseProjectPage(PageObject):
    body    = PageElement(tag_name='body')
    logout  = PageElement(link_text='LOG OUT')
    sidebar = PageElement(id_="sidebar")
    sidebar_hide = PageElement(class_name='js-hide-sidebar')
    sidebar_show = PageElement(class_name='js-show-sidebar')
