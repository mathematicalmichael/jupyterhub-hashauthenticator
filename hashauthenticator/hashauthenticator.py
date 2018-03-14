import csv

from jupyterhub import orm
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import admin_only
from oauthenticator.google import GoogleOAuthenticator
from tornado import gen
from tornado.httputil import url_concat
from tornado.web import Finish
from traitlets import Unicode, Integer, Bool

from .passwordhash import generate_password_digest


class PasswordHandler(BaseHandler):

  def initialize(self, get_password):
    self.get_password = get_password

  @admin_only
  def get(self):
    users = sorted((u.name, self.get_password(u.name)) for u in self.db.query(orm.User))
    self.set_header('content-type', 'text/plain')
    csv.writer(self).writerows(users)


class HashAuthenticator(GoogleOAuthenticator):
  secret_key = Unicode(
    config=True,
    help="Key used to encrypt usernames to produce passwords."
  )

  password_length = Integer(
    default_value=6,
    config=True,
    help="Password length.")

  show_logins = Bool(
    default_value=False,
    config=True,
    help="Display login information to admins at /hub/login_list."
  )

  def get_password(self, username):
    return generate_password_digest(username, self.secret_key, self.password_length)

  @gen.coroutine
  def authenticate(self, handler, data):
    if not data:
      retval = yield super().authenticate(handler, data)
      retval['name'] += '@'
      retval['admin'] = True
      return retval

    username = data['username']
    password = data['password']

    if username.endswith('@'):
      handler.redirect(url_concat(self.login_url(handler.hub.base_url),
                                  {'next': handler.get_argument('next', '')}))
      raise Finish

    if password == self.get_password(username):
      return username

    return None

  def get_handlers(self, app):
    extra_handers = []
    if self.show_logins:
      extra_handers = [('/login_list', PasswordHandler, {'get_password': self.get_password})]

    return super().get_handlers(app) + extra_handers
