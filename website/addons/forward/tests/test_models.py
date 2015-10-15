# -*- coding: utf-8 -*-

from nose.tools import *  # PEP8 asserts

from modularodm.exceptions import ValidationError

from tests.base import OsfTestCase
from website.addons.forward.tests.factories import ForwardSettingsFactory


class TestSettingsValidation(OsfTestCase):

    def setUp(self):
        super(TestSettingsValidation, self).setUp()
        self.settings = ForwardSettingsFactory()

    def test_validate_url_bad(self):
        self.settings.url = 'badurl'
        with assert_raises(ValidationError):
            self.settings.save()

    def test_validate_url_good(self):
        self.settings.url = 'http://frozen.pizza.reviews/'
        try:
            self.settings.save()
        except ValidationError:
            assert 0

    def test_validate_redirect_bool_bad(self):
        self.settings.redirect_bool = 'notabool'
        with assert_raises(ValidationError):
            self.settings.save()

    def test_validate_redirect_bool_good(self):
        self.settings.redirect_bool = False
        try:
            self.settings.save()
        except ValidationError:
            assert 0

    def test_validate_redirect_secs_bad(self):
        self.settings.redirect_secs = -2
        with assert_raises(ValidationError):
            self.settings.save()

    def test_validate_redirect_secs_good(self):
        self.settings.redirect_secs = 20
        try:
            self.settings.save()
        except ValidationError:
            assert 0

    def test_label_sanitary(self):
        self.settings.label = 'safe'
        try:
            self.settings.save()
        except ValidationError:
            assert False

    def test_label_unsanitary(self):
        self.settings.label = 'un<br />safe'
        with assert_raises(ValidationError):
            self.settings.save()
