# -*- coding: utf-8 -*-
from selenium.webdriver.support.ui import Select
from page_objects import PageObject, PageElement, MultiPageElement

class SettingsPage(PageObject):
    return_link = PageElement(css='#sidebar-brand a')
    inlist_delete_confirm = PageElement(name='inlist_delete_confirm')
    action_delete_confirm = PageElement(name='action_delete_confirm')
    confirm     = PageElement(name='confirm')
    content     = PageElement(id_='content')
    sidebar     = PageElement(id_='sidebar')
    sidebar_return_link = PageElement(css='#sidebar a#return')
    account_link = PageElement(css='a#account')
    menu        = PageElement(name='menu')
    logout      = PageElement(name='logout')

    _settings_list = MultiPageElement(tag_name='label')
    @property
    def settings_list(self):
        return [setting.text for setting in self._settings_list]

    _language_elem = PageElement(name='language')
    @property
    def language(self):
        return Select(self._language_elem)


class AccountSettingsPage(PageObject):
    change_password = PageElement(css='a#changepwd')


class ChangePasswordPage(PageObject):
    old_password = PageElement(name='oldpassword')
    password1    = PageElement(name='password1')
    password2    = PageElement(name='password2')
    confirm      = PageElement(xpath="//form//button[@type='submit']")
