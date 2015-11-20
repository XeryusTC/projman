# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class InlistPage(PageObject):
    add_box     = PageElement(name='text')
    add_button  = PageElement(xpath="//form//input[@id='submit-id-submit']")
    thelist     = MultiPageElement(xpath="//table[@id='list']//tr/td[1]")
    listrows    = MultiPageElement(xpath="//table[@id='list']//tr")
    error_lists = MultiPageElement(css='.errorlist')
    delete_item = PageElement(link_text='DELETE', context=True)


class InlistDeletePage(PageObject):
    confirm = PageElement(xpath="//input[@type='submit']")
