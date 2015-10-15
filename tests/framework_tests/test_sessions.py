from nose.tools import *

from framework.sessions import utils
from tests import factories
from tests.base import DbTestCase
from website.models import User
from website.models import Session


class SessionUtilsTestCase(DbTestCase):
    def setUp(self, *args, **kwargs):
        super(SessionUtilsTestCase, self).setUp(*args, **kwargs)
        self.user = factories.UserFactory()

    def tearDown(self, *args, **kwargs):
        super(SessionUtilsTestCase, self).tearDown(*args, **kwargs)
        User.remove()
        Session.remove()

    def test_remove_session_for_user(self):
        factories.SessionFactory(user=self.user)

        # sanity check
        assert_equal(1, Session.find().count())

        utils.remove_sessions_for_user(self.user)
        assert_equal(0, Session.find().count())

        factories.SessionFactory()
        factories.SessionFactory(user=self.user)

        # sanity check
        assert_equal(2, Session.find().count())

        utils.remove_sessions_for_user(self.user)
        assert_equal(1, Session.find().count())
