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
        self.assertIn('hide-sidebar', page.body.get_attribute('class'))

        # When clicking the hide button again the sidebar reappears
        page.sidebar_hide.click()
        self.assertNotIn('hide-sidebar',
            page.body.get_attribute('class'))

    def test_sidebar_can_be_toggled_in_small_window_mode(self):
        # Alice is a logged in user
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        self.is_logged_in()
        self.browser.set_window_size(480, 800)

        # The sidebar should not be active
        page = pages.project.BaseProjectPage(self.browser)
        self.wait_for(lambda: self.assertEqual(page.sidebar.location['x'],
            -200))
        self.assertNotIn('active', page.sidebar.get_attribute('class'))

        oldpos = page.sidebar_show.location

        # When clicking the show button the hidebar appears
        page.sidebar_show.click()
        self.wait_for(lambda: self.assertEqual(page.sidebar.location['x'], 0))
        # The rest of the page stayed the same and is behind an overlay
        self.assertEqual(oldpos, page.sidebar_show.location)
        self.assertTrue(page.overlay.is_displayed())

        # When clicking the overlay the sidebar disappears again
        page.overlay.click()
        self.wait_for(lambda: self.assertEqual(page.sidebar.location['x'],
            -200))
        self.assertIsNone(page.overlay)
