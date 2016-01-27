# -*- coding: utf-8 -*-
from selenium.webdriver.support.ui import Select
from page_objects import PageObject, PageElement, MultiPageElement

class SettingsPage(PageObject):
    return_link = PageElement(css='a.mui--text-title.appbar-correct')
    inlist_delete_confirm = PageElement(name='inlist_delete_confirm')
    action_delete_confirm = PageElement(name='action_delete_confirm')
    confirm     = PageElement(name='confirm')
    content     = PageElement(id_='content')

    _settings_list = MultiPageElement(tag_name='label')
    @property
    def settings_list(self):
        return [setting.text for setting in self._settings_list]

    _language_elem = PageElement(name='language')
    @property
    def language(self):
        return Select(self._language_elem)
