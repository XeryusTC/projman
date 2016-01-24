# -*- coding: utf-8 -*-

from page_objects import PageObject, PageElement

class SettingsPage(PageObject):
    return_link = PageElement(css='a.mui--text-title.appbar-correct')
