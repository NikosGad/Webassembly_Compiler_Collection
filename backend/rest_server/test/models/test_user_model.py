import datetime
import unittest

from rest_server.models import user_model

class UserModelNoRecordCreationTestCase(unittest.TestCase):
    """Testcase for methods of models/user_model.py module that do not need user creation in DB."""
    def setUp(self):
        self.user_info = {
            "username": "test_username",
            "password": "test_password",
            "email": "test_email",
        }

    def test_init(self):
        test_user = user_model.User(**self.user_info)

        self.assertEqual(test_user.username, self.user_info["username"])
        self.assertNotEqual(test_user.password, self.user_info["password"])
        self.assertTrue(test_user.validate_password(self.user_info["password"]))
        self.assertEqual(test_user.email, self.user_info["email"])
        self.assertIsInstance(test_user.created_at, datetime.datetime)
        self.assertIsInstance(test_user.updated_at, datetime.datetime)

    def test_get_user_by_username__no_user_exists(self):
        test_user_db = user_model.User.get_user_by_username(self.user_info["username"])

        self.assertIsNone(test_user_db)

    def test_get_user_by_username__no_user_exists(self):
        test_user_db = user_model.User.get_user_by_email(self.user_info["email"])

        self.assertIsNone(test_user_db)

    def test_get_all_users__no_users_exist(self):
        test_users_all_db = user_model.User.get_all_users()

        self.assertEqual(test_users_all_db, [])

class UserModelTestCase(unittest.TestCase):
    """Testcase for methods of models/user_model.py module that need user creation in DB."""
    @classmethod
    def setUpClass(cls):
        cls.user_info_1 = {
            "username": "test_username_1",
            "password": "test_password_1",
            "email": "test_email_1",
        }

        cls.user_info_2 = {
            "username": "test_username_2",
            "password": "test_password_2",
            "email": "test_email_2",
        }

        cls.test_user_1 = user_model.User(**cls.user_info_1)
        cls.test_user_1.id = cls.user_info_1["id"] = 1
        cls.test_user_2 = user_model.User(**cls.user_info_2)
        cls.test_user_2.id = cls.user_info_2["id"] = 2

        cls.test_user_1.create()
        cls.test_user_2.create()

    @classmethod
    def tearDownClass(cls):
        cls.test_user_1.delete()
        cls.test_user_2.delete()

    def test_get_user_by_username__user_exists(self):
        test_user_1_db = user_model.User.get_user_by_username(self.user_info_1["username"])

        self.assertIsNotNone(test_user_1_db)
        self.assertEqual(test_user_1_db.id, self.user_info_1["id"])
        self.assertEqual(test_user_1_db.username, self.user_info_1["username"])
        self.assertNotEqual(test_user_1_db.password, self.user_info_1["password"])
        self.assertTrue(test_user_1_db.validate_password(self.user_info_1["password"]))
        self.assertEqual(test_user_1_db.email, self.user_info_1["email"])
        self.assertIsInstance(test_user_1_db.created_at, datetime.datetime)
        self.assertIsInstance(test_user_1_db.updated_at, datetime.datetime)

    def test_get_user_by_email__user_exists(self):
        test_user_1_db = user_model.User.get_user_by_email(self.user_info_1["email"])

        self.assertIsNotNone(test_user_1_db)
        self.assertEqual(test_user_1_db.id, self.user_info_1["id"])
        self.assertEqual(test_user_1_db.username, self.user_info_1["username"])
        self.assertNotEqual(test_user_1_db.password, self.user_info_1["password"])
        self.assertTrue(test_user_1_db.validate_password(self.user_info_1["password"]))
        self.assertEqual(test_user_1_db.email, self.user_info_1["email"])
        self.assertIsInstance(test_user_1_db.created_at, datetime.datetime)
        self.assertIsInstance(test_user_1_db.updated_at, datetime.datetime)

    def test_get_all_users__users_exist(self):
        test_users_all_db = user_model.User.get_all_users()

        self.assertIsInstance(test_users_all_db, list)
        self.assertEqual(len(test_users_all_db), 2, msg="Users list has length different than 2")
        self.assertTrue(test_users_all_db == [self.test_user_2, self.test_user_1] or test_users_all_db == [self.test_user_1, self.test_user_2],
            msg="get_all_users test\nReturned: {returned}\nExpected: [{user_1}, {user_2}] or [{user_2}, {user_1}]".format(
                returned=test_users_all_db,
                user_1=self.test_user_1,
                user_2=self.test_user_2
            )
        )

    class UserModelPrimaryKeyAutoIncrementTestCase(unittest.TestCase):
        """Testcase to check the auto increment of the primary key in DB of models/user_model.py module."""
        def setUp(self):
            self.user_info_1 = {
                "username": "test_username_1",
                "password": "test_password_1",
                "email": "test_email_1",
            }

            self.user_info_2 = {
                "username": "test_username_2",
                "password": "test_password_2",
                "email": "test_email_2",
            }

            self.test_user_1 = user_model.User(**self.user_info_1)
            self.test_user_2 = user_model.User(**self.user_info_2)

            self.test_user_1.create()
            self.test_user_2.create()

        def tearDown(self):
            self.test_user_1.delete()
            self.test_user_2.delete()

        def test_user_primary_key_auto_increment(self):
            test_user_1_db = user_model.User.get_user_by_username(self.user_info_1["username"])
            test_user_2_db = user_model.User.get_user_by_username(self.user_info_2["username"])

            self.assertEqual(abs(test_user_1_db.id - test_user_2_db.id), 1)
