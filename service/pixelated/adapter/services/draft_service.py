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
from twisted.internet import defer
from pixelated.adapter.errors import DuplicatedDraftException


class DraftService(object):
    __slots__ = '_mail_store'

    def __init__(self, mail_store):
        self._mail_store = mail_store

    @defer.inlineCallbacks
    def create_draft(self, input_mail):
        mail = yield self._mail_store.add_mail('DRAFTS', input_mail.raw)
        defer.returnValue(mail)

    @defer.inlineCallbacks
    def update_draft(self, ident, input_mail):
        new_draft = yield self.create_draft(input_mail)
        try:
            yield self._mail_store.delete_mail(ident)
            defer.returnValue(new_draft)
        except Exception as error:
            errorMessage = error.args[0].getErrorMessage()

            if errorMessage == 'Need to create doc before deleting':
                yield self._mail_store.delete_mail(new_draft.ident)
            raise DuplicatedDraftException(errorMessage)
