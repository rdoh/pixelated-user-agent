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
from leap.mail.outgoing.service import OutgoingMail
from twisted.mail.smtp import User
from twisted.trial import unittest

from mockito import mock, when, verify, any, unstub
from pixelated.adapter.services.mail_sender import MailSender, MailSenderException
from pixelated.adapter.model.mail import InputMail
from pixelated.bitmask_libraries.smtp import LeapSMTPConfig
from pixelated.support.functional import flatten
from test.support.test_helper import mail_dict
from twisted.internet import reactor, defer
from twisted.internet.defer import Deferred
from mockito.matchers import Matcher


class TwistedSmtpUserCapture(Matcher):

    def __init__(self, username):
        self._username = username

    def matches(self, arg):
        return isinstance(arg, User) \
            and isinstance(arg.dest.addrstr, str) \
            and self._username == arg.dest.addrstr


class MailSenderTest(unittest.TestCase):

    def setUp(self):
        self._cert_path = u'/some/cert/path'
        self._keymanager_mock = mock()
        self._remote_smtp_host = 'some.host.test'
        self._remote_smtp_port = 1234
        self._smtp_config = LeapSMTPConfig('someone@somedomain.tld', self._cert_path, self._remote_smtp_host, self._remote_smtp_port)

    def tearDown(self):
        unstub()

    @defer.inlineCallbacks
    def test_iterates_over_recipients(self):
        sender = MailSender(self._smtp_config, self._keymanager_mock)
        input_mail = InputMail.from_dict(mail_dict())

        when(OutgoingMail).send_message(any(), any()).thenAnswer(lambda: defer.succeed(None))

        yield sender.sendmail(input_mail)

        for recipient in flatten([input_mail.to, input_mail.cc, input_mail.bcc]):
            verify(OutgoingMail).send_message(any(), TwistedSmtpUserCapture(recipient))

    @defer.inlineCallbacks
    def test_problem_with_email_raises_exception(self):
        sender = MailSender(self._smtp_config, self._keymanager_mock)
        input_mail = InputMail.from_dict(mail_dict())

        when(OutgoingMail).send_message(any(), any()).thenAnswer(lambda: defer.fail(Exception('pretend something went wrong')))

        try:
            yield sender.sendmail(input_mail)
            self.fail('Exception expected!')
        except MailSenderException, e:
            for recipient in flatten([input_mail.to, input_mail.cc, input_mail.bcc]):
                self.assertTrue(recipient in e.email_error_map)
