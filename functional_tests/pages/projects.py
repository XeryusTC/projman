# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class BaseProjectPage(PageObject):
    body    = PageElement(tag_name='body')
    content = PageElement(id_='content')
    logout  = PageElement(link_text='LOG OUT')
    overlay = PageElement(id_='mui-overlay')
    sidebar = PageElement(id_="sidebar")
    sidebar_hide = PageElement(class_name='js-hide-sidebar')
    sidebar_show = PageElement(class_name='js-show-sidebar')

    inlist_link = PageElement(link_text='In list', context=True)
    action_link = PageElement(link_text='Actions', context=True)
    create_project_link = PageElement(link_text='Create project', context=True)

    _project_links = MultiPageElement(css="a.project", context=True)
    def project_link(self, text):
        for link in self._project_links(self.sidebar):
            if text == link.text:
                return link


class InlistPage(PageObject):
    add_box     = PageElement(name='text')
    add_button  = PageElement(xpath="//form//input[@id='submit-id-submit']")
    thelist     = MultiPageElement(css='#list .full-height')
    listrows    = MultiPageElement(css='#list .mui-row')
    error_lists = MultiPageElement(css='.errorlist')
    delete_item = PageElement(class_name='action-delete', context=True)
    convert_action = PageElement(class_name='action-convert', context=True)
    convert_project = PageElement(class_name='action-project', context=True)


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
    _delete_item = PageElement(class_name='action-delete', context=True)

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


class CreateProjectPage(PageObject):
    name_box        = PageElement(name='name')
    description_box = PageElement(name='description')
    create_button   = PageElement(name='create')
    error_lists     = MultiPageElement(css='.errorlist')


class ProjectPage(PageObject):
    info       = PageElement(id_='info')
    add_box    = PageElement(name='text')
    add_button = PageElement(xpath="//form//input[@name='submit']")
    edit       = PageElement(css='.action-edit')
    delete     = PageElement(class_name='delete-project')
    thelist    = MultiPageElement(css='#list .mui-row')
    checked_list = MultiPageElement(css='#list .mui-row.checked')
    error_lists  = MultiPageElement(css='.errorlist')

    _list_text   = PageElement(css='.action-item', context=True)
    _delete_item = PageElement(class_name='action-delete', context=True)

    def list_text(self, context):
        return [self._list_text(row).text for row in context]

    def get_list_rows(self, context):
        res = {}
        for i in range(len(context)):
            res[i] = {'text': self._list_text(context[i]),
                'delete': self._delete_item(context[i])}
        return res


class EditPage(PageObject):
    name        = PageElement(name='name')
    description = PageElement(name='description')
    confirm     = PageElement(name='update')


class ProjectDeletePage(PageObject):
    content = PageElement(id_='content')
    confirm = PageElement(xpath="//input[@value='Confirm']")
