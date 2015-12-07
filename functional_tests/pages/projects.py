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
    delete_item = PageElement(class_name='action-delete', context=True)
    convert_action = PageElement(class_name='action-convert', context=True)


class InlistDeletePage(PageObject):
    content = PageElement(id_='content')
    confirm = PageElement(xpath="//input[@type='submit']")


class ActionlistPage(PageObject):
    add_box     = PageElement(name='text')
    add_button  = PageElement(xpath="//form//input[@id='submit-id-submit']")
    error_lists = MultiPageElement(css='.errorlist')
    thelist     = MultiPageElement(css='#list .mui-row')
    checked_list = MultiPageElement(css='#checked .mui-row')

    _list_text  = PageElement(css='.full-height', context=True)
    _delete_item = PageElement(link_text='DELETE', context=True)

    def list_text(self, context):
        text = [self._list_text(row).text for row in context]
        return text

    def get_list_rows(self, context):
        res = {}
        for i in range(len(context)):
            res[i] = {'text': self._list_text(context[i]),
                'delete': self._delete_item(context[i])}
        return res


class ActionDeletePage(PageObject):
    content = PageElement(id_='content')
    confirm = PageElement(xpath="//input[@type='submit']")


class ConvertToActionPage(PageObject):
    text_box = PageElement(name='text')
    convert_button = PageElement(xpath="//input[@type='submit']")
