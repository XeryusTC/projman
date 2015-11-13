# -*- coding: utf-8 -*-
from page_objects import PageObject, PageElement, MultiPageElement

class LoginPage(PageObject):
    username = PageElement(name='login')
    password = PageElement(name='password')
    remember = PageElement(name='remember')
    signin   = PageElement(xpath="//form[@class='login']//button")
    forgot   = PageElement(partial_link_text='FORGOT')
    register = PageElement(link_text="REGISTER")

    # Social media buttons
    persona = PageElement(link_text='PERSONA')


class RegisterPage(PageObject):
    username  = PageElement(name='username')
    password1 = PageElement(name='password1')
    password2 = PageElement(name='password2')
    email     = PageElement(name='email')
    signup    = PageElement(xpath="//form[@class='signup']//button")
    errors    = MultiPageElement(class_name='errorlist')


class PasswordResetPage(PageObject):
    email = PageElement(name='email')
    reset = PageElement(xpath="//form[@class='password_reset']//button")


class ConfirmEmailPage(PageObject):
    body    = PageElement(tag_name='body')
    confirm = PageElement(tag_name='button')


class LogoutPage(PageObject):
    signout = PageElement(xpath="//form//button")


class PasswordResetDonePage(PageObject):
    body = PageElement(tag_name='body')


class ResetPasswordKeyPage(PageObject):
    password1 = PageElement(name='password1')
    password2 = PageElement(name='password2')
    submit    = PageElement(name='action')


class ResetPasswordKeyDonePage(PageObject):
    signin = PageElement(link_text="sign in")

class LogoutConfirmPage(PageObject):
    confirm = PageElement(xpath="//form//button")
