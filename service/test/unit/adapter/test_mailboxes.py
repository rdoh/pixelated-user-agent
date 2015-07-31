#
# Copyright (c) 2014 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
import unittest

from pixelated.adapter.model.mail import PixelatedMail
from pixelated.adapter.services.mailboxes import Mailboxes
from mockito import mock, when, verify, any as ANY
from twisted.internet import defer
from test.support import test_helper
from mock import MagicMock


class PixelatedMailboxesTest(unittest.TestCase):

    def setUp(self):
        self.querier = mock()
        self.mail_store = mock()
        self.search_engine = mock()
        self.account = MagicMock()
        self.mailboxes = Mailboxes(self.account, self.mail_store, self.querier, self.search_engine)

    @defer.inlineCallbacks
    def test_move_to_inbox(self):
        mail = PixelatedMail.from_soledad(*test_helper.leap_mail(), soledad_querier=self.querier)
        when(self.mail_store).mail(1).thenReturn(defer.succeed(mail))
        when(self.mail_store).update_mail(ANY()).thenReturn(defer.succeed(None))

        mail.set_mailbox('TRASH')
        recovered_mail = yield self.mailboxes.move_to_inbox(1)
        self.assertEquals('INBOX', recovered_mail.mailbox_name)
        verify(mail).save()
