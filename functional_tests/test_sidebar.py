# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model

from . import pages, remote
from .base import FunctionalTestCase

User = get_user_model()

class SidebarTests(FunctionalTestCase):
    def test_sidebar_can_be_toggled_in_large_window_mode(self):
        # Alice is a logged in user
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        self.is_logged_in()
        self.browser.set_window_size(1200, 800)

        # The sidebar should be active
        page = pages.project.BaseProjectPage(self.browser)
        self.assertTrue(page.sidebar.is_displayed())
        self.assertGreaterEqual(page.sidebar.location['x'], 0)

        # When clicking the hide button the sidebar disappears
        page.sidebar_hide.click()
        self.assertIn('hide-sidebar', page.sidebar.css.get_attribute('class'))

        # When clicking the hide button again the sidebar reappears
        page.sidebar_hide.click()
        self.assertNotIn('hide-sidebar',
            page.sidebar.css.get_attribute('class'))

    def test_sidebar_can_be_toggled_in_small_window_mode(self):
        # Alice is a logged in user
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        self.is_logged_in()
        self.browser.set_window_size(480, 800)

        # The sidebar should not be active
        page = pages.project.BaseProjectPage(self.browser)
        self.assertFalse(page.sidebar.is_displayed())
        self.assertNotIn('show-sidebar',
            page.sidebar.css.get_attribute('class'))

        # When clicking the show button the hidebar appears
        page.sidebar_show.click()
        self.assertIn('show-sidebar', page.sidebar.css.get_attribute('class'))

        # When click the show button again the hidebar disappears again
        page.sidebar-show.click()
        self.assertNotIn('show-sidebar',
            page.sidebar.css.get_attribute('class'))