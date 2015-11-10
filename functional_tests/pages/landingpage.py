# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class LandingPage(PageObject):
    branding      = PageElement(xpath="//header//a[@href='/en/']")
    header_signin = PageElement(xpath="//header//a[@class='mui-btn']")
    body_signin   = PageElement(xpath="//div[@id='content']//a['Sign in']")
    scripts       = MultiPageElement(tag_name='script')
    stylesheets   = MultiPageElement(tag_name='link')
