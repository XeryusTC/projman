# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement

class BaseProjectPage(PageObject):
    body    = PageElement(tag_name='body')
    logout  = PageElement(link_text='LOG OUT')
    overlay = PageElement(id_='mui-overlay')
    sidebar = PageElement(id_="sidebar")
    sidebar_hide = PageElement(class_name='js-hide-sidebar')
    sidebar_show = PageElement(class_name='js-show-sidebar')

    inlist_link = PageElement(link_text='In list', context=True)
    action_link = PageElement(link_text='Actions', context=True)
