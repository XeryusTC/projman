# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class BaseProjectPage(PageObject):
    body    = PageElement(tag_name='body')
    logout  = PageElement(link_text='LOG OUT')
    overlay = PageElement(id_='mui-overlay')
    sidebar = PageElement(id_="sidebar")
    sidebar_hide = PageElement(class_name='js-hide-sidebar')
    sidebar_show = PageElement(class_name='js-show-sidebar')

    inlist_link = PageElement(link_text='In list', context=True)
    action_link = PageElement(link_text='Actions', context=True)


class InlistPage(PageObject):
    add_box     = PageElement(name='text')
    add_button  = PageElement(xpath="//form//input[@id='submit-id-submit']")
    thelist     = MultiPageElement(css='#list .full-height')
    listrows    = MultiPageElement(css='#list .mui-row')
    error_lists = MultiPageElement(css='.errorlist')
    delete_item = PageElement(link_text='DELETE', context=True)


class InlistDeletePage(PageObject):
    content = PageElement(id_='content')
    confirm = PageElement(xpath="//input[@type='submit']")


class ActionlistPage(PageObject):
    add_box     = PageElement(name='text')
    add_button  = PageElement(xpath="//form//input[@id='submit-id-submit']")
    error_lists = MultiPageElement(css='.errorlist')
    thelist     = MultiPageElement(css='#list .mui-row')

    _list_text  = PageElement(css='.full-height', context=True)

    @property
    def list_text(self):
        text = [self._list_text(row).text for row in self.thelist]
        return text
