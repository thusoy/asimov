import unittest

from asimov import create_app


# class UserTestCase(unittest.TestCase):
#     """ Test case with a temp db and three users available: admin_user, anon_user and auth_user,
#     representing unauthenticated users, like random passerbys, authenticated users, which have
#     authenticated with Facebook, but nothing more, and admin users, which is basically me.
#     More user types might be added later.
#     """

#     def create_test_client(self, user):
#         """ Create a test client with the permissions and an active session of the given user. """
#         with self.app.test_request_context():
#             db.session.add(user)
#             db.session.commit()

#             # Login the user and save the session
#             login_user(user)
#             session_copy = session.copy()

#         # Re-create the session with a new test client
#         with self.app.test_client() as c:
#             with c.session_transaction() as sess:
#                 for k, v in session_copy.items():
#                     sess[k] = v
#             return c


#     def pre_set_up(self):
#         self.app = create_app(SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
#             WTF_CSRF_ENABLED=False, SECRET_KEY='bogus')
#         with self.app.app_context():
#             db.create_all()
#         self.admin_user = self.create_test_client(User(first_name='Bob', last_name='Admin', is_admin=True))
#         self.anon_user = self.app.test_client()
#         self.auth_user = self.create_test_client(User(first_name='Alice', last_name='User'))


#     def __call__(self, *args, **kwargs):
#         self.pre_set_up()
#         super(UserTestCase, self).__call__(*args, **kwargs)
#         self.post_tear_down()


#     @ignore(OSError)
#     def post_tear_down(self):
#         os.remove(self.test_db.name)
