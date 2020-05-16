import datetime
import unittest

from rest_server.models import file_model, user_model

class FileModelNoRecordCreationTestCase(unittest.TestCase):
    """Testcase for methods of models/file_model.py module that do not need file creation in DB."""
    def setUp(self):
        self.file_info = {
            "user_id":              1,
            "name":                 "test_name",
            "directory":            "test_directory",
            "compilation_options":  ["option1", "option2", "option3"],
            "language":             "test_language",
            "status":               "test_status",
        }

    def test_init(self):
        test_file = file_model.SourceCodeFile(**self.file_info)

        self.assertEqual(test_file.user_id, self.file_info["user_id"])
        self.assertEqual(test_file.name, self.file_info["name"])
        self.assertEqual(test_file.directory, self.file_info["directory"])
        self.assertEqual(test_file.compilation_options, self.file_info["compilation_options"])
        self.assertEqual(test_file.language, self.file_info["language"])
        self.assertEqual(test_file.status, self.file_info["status"])
        self.assertIsInstance(test_file.created_at, datetime.datetime)
        self.assertIsInstance(test_file.updated_at, datetime.datetime)

    def test_get_file_by_file_id_and_user_id__no_file_exists(self):
        test_file_db = file_model.SourceCodeFile.get_file_by_file_id_and_user_id(1, 1)

        self.assertIsNone(test_file_db)

    def test_get_files_per_language_by_user_id__no_files_exist(self):
        db_result = file_model.SourceCodeFile.get_files_per_language_by_user_id(1)

        self.assertEqual(db_result, [])

    def test_get_files_per_language_by_user_id_as_json__no_files_exist(self):
        test_files_json_db = file_model.SourceCodeFile.get_files_per_language_by_user_id_as_json(1)

        self.assertIsNone(test_files_json_db)

    def test_get_all_files__no_files_exist(self):
        db_all_files_list = file_model.SourceCodeFile.get_all_files()

        self.assertEqual(db_all_files_list, [])

class FileModelTestCase(unittest.TestCase):
    """Testcase for methods of models/file_model.py module that need file creation in DB."""
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

        cls.file_info_1 = {
            "user_id":              1,
            "name":                 "test_name_1",
            "directory":            "test_directory_1",
            "compilation_options":  ["option1", "option2", "option3"],
            "language":             "test_language_1",
            "status":               "test_status_1",
        }

        cls.file_info_2 = {
            "user_id":              1,
            "name":                 "test_name_2",
            "directory":            "test_directory_2",
            "compilation_options":  ["option1", "option2", "option3"],
            "language":             "test_language_1",
            "status":               "test_status_2",
        }

        cls.file_info_3 = {
            "user_id":              1,
            "name":                 "test_name_3",
            "directory":            "test_directory_3",
            "compilation_options":  ["option1", "option2", "option3"],
            "language":             "test_language_2",
            "status":               "test_status_1",
        }

        cls.file_info_4 = {
            "user_id":              2,
            "name":                 "test_name_2",
            "directory":            "test_directory_4",
            "compilation_options":  ["option1", "option2", "option3"],
            "language":             "test_language_2",
            "status":               "test_status_2",
        }

        cls.test_user_1 = user_model.User(**cls.user_info_1)
        cls.test_user_1.id = cls.user_info_1["id"] = 1
        cls.test_user_2 = user_model.User(**cls.user_info_2)
        cls.test_user_2.id = cls.user_info_2["id"] = 2

        cls.test_file_1 = file_model.SourceCodeFile(**cls.file_info_1)
        cls.test_file_1.id = cls.file_info_1["id"] = 1
        cls.test_file_2 = file_model.SourceCodeFile(**cls.file_info_2)
        cls.test_file_2.id = cls.file_info_2["id"] = 2
        cls.test_file_3 = file_model.SourceCodeFile(**cls.file_info_3)
        cls.test_file_3.id = cls.file_info_3["id"] = 3
        cls.test_file_4 = file_model.SourceCodeFile(**cls.file_info_4)
        cls.test_file_4.id = cls.file_info_4["id"] = 4

        cls.test_user_1.create()
        cls.test_user_2.create()
        cls.test_file_1.create()
        cls.test_file_2.create()
        cls.test_file_3.create()
        cls.test_file_4.create()

    @classmethod
    def tearDownClass(cls):
        cls.test_file_1.delete()
        cls.test_file_2.delete()
        cls.test_file_3.delete()
        cls.test_file_4.delete()
        cls.test_user_1.delete()
        cls.test_user_2.delete()

    def test_get_file_by_file_id_and_user_id__file_exists(self):
        db_file_1 = file_model.SourceCodeFile.get_file_by_file_id_and_user_id(self.test_file_1.id, self.test_file_1.user_id)

        self.assertEqual(db_file_1, self.test_file_1,
            msg="Files are different.\nReturned: {returned}\nExpected: {expected}".format(
                returned=db_file_1,
                expected=self.test_file_1
            )
        )

    def test_get_files_per_language_by_user_id__files_exist(self):
        db_result = file_model.SourceCodeFile.get_files_per_language_by_user_id(self.test_user_1.id)

        self.assertIsInstance(db_result, list)
        self.assertEqual(len(db_result), 2,
            msg="List of languages has length different than 2\nReturned: {returned}".format(
                returned=db_result
            )
        )

        db_tuple_1 = db_result[0]
        db_tuple_2 = db_result[1]

        self.assertIsInstance(db_tuple_1, tuple)
        self.assertEqual(len(db_tuple_1), 2,
            msg="The tuple should contain only 2 elements: the language and the list of files as dictionaries\nReturned: {returned}".format(
                returned=db_tuple_1
            )
        )
        self.assertIsInstance(db_tuple_2, tuple)
        self.assertEqual(len(db_tuple_2), 2,
            msg="The tuple should contain only 2 elements: the language and the list of files as dictionaries\nReturned: {returned}".format(
                returned=db_tuple_2
            )
        )

        db_language_1 = db_tuple_1[0]
        db_language_1_files = db_tuple_1[1]
        db_language_2 = db_tuple_2[0]
        db_language_2_files = db_tuple_2[1]

        self.assertEqual(db_language_1, "test_language_1")
        self.assertIsInstance(db_language_1_files, list)
        self.assertEqual(len(db_language_1_files), 2)
        self.assertEqual(db_language_2, "test_language_2")
        self.assertIsInstance(db_language_2_files, list)
        self.assertEqual(len(db_language_2_files), 1)

        db_file_1_dict = db_language_1_files[0]
        db_file_2_dict = db_language_1_files[1]
        db_file_3_dict = db_language_2_files[0]

        db_file_dict_list = [db_file_1_dict, db_file_2_dict, db_file_3_dict]
        test_file_list = [self.test_file_1, self.test_file_2, self.test_file_3]

        for i in range(3):
            self.assertEqual(db_file_dict_list[i]["id"], test_file_list[i].id)
            self.assertEqual(db_file_dict_list[i]["user_id"], test_file_list[i].user_id)
            self.assertEqual(db_file_dict_list[i]["name"], test_file_list[i].name)
            self.assertEqual(db_file_dict_list[i]["directory"], test_file_list[i].directory)
            self.assertEqual(db_file_dict_list[i]["compilation_options"], test_file_list[i].compilation_options)
            self.assertEqual(db_file_dict_list[i]["language"], test_file_list[i].language)
            self.assertEqual(db_file_dict_list[i]["status"], test_file_list[i].status)
            self.assertIsInstance(db_file_dict_list[i]["created_at"], str, msg="json_agg should convert the datetime to string")
            self.assertIsInstance(db_file_dict_list[i]["updated_at"], str, msg="json_agg should convert the datetime to string")

    def test_get_files_per_language_by_user_id_as_json__files_exist(self):
        db_result = file_model.SourceCodeFile.get_files_per_language_by_user_id_as_json(self.test_user_1.id)

        self.assertIsInstance(db_result, dict)
        self.assertEqual(len(db_result.keys()), 2,
            msg="Dictionary does not have exactly 2 different languages\nReturned: {returned}".format(
                returned=db_result
            )
        )
        self.assertIn("test_language_1", db_result.keys())
        self.assertIn("test_language_2", db_result.keys())

        db_language_1_files = db_result["test_language_1"]
        db_language_2_files = db_result["test_language_2"]

        self.assertIsInstance(db_language_1_files, list)
        self.assertEqual(len(db_language_1_files), 2)
        self.assertIsInstance(db_language_2_files, list)
        self.assertEqual(len(db_language_2_files), 1)

        db_file_1_dict = db_language_1_files[0]
        db_file_2_dict = db_language_1_files[1]
        db_file_3_dict = db_language_2_files[0]

        db_file_dict_list = [db_file_1_dict, db_file_2_dict, db_file_3_dict]
        test_file_list = [self.test_file_1, self.test_file_2, self.test_file_3]

        for i in range(3):
            self.assertEqual(db_file_dict_list[i]["id"], test_file_list[i].id)
            self.assertEqual(db_file_dict_list[i]["user_id"], test_file_list[i].user_id)
            self.assertEqual(db_file_dict_list[i]["name"], test_file_list[i].name)
            self.assertEqual(db_file_dict_list[i]["directory"], test_file_list[i].directory)
            self.assertEqual(db_file_dict_list[i]["compilation_options"], test_file_list[i].compilation_options)
            self.assertEqual(db_file_dict_list[i]["language"], test_file_list[i].language)
            self.assertEqual(db_file_dict_list[i]["status"], test_file_list[i].status)
            self.assertIsInstance(db_file_dict_list[i]["created_at"], str, msg="json_agg should convert the datetime to string")
            self.assertIsInstance(db_file_dict_list[i]["updated_at"], str, msg="json_agg should convert the datetime to string")

    def test_get_all_files__files_exist(self):
        db_result = file_model.SourceCodeFile.get_all_files()

        self.assertIsInstance(db_result, list)
        self.assertEqual(len(db_result), 4,
            msg="List of languages has length different than 4\nReturned: {returned}".format(
                returned=db_result
            )
        )

        db_file_1 = db_result[0]
        db_file_2 = db_result[1]
        db_file_3 = db_result[2]
        db_file_4 = db_result[3]

        self.assertEqual(db_file_1, self.test_file_1)
        self.assertEqual(db_file_2, self.test_file_2)
        self.assertEqual(db_file_3, self.test_file_3)
        self.assertEqual(db_file_4, self.test_file_4)

class FileModelPrimaryKeyAutoIncrementTestCase(unittest.TestCase):
    """Testcase to check the auto increment of the primary key in DB of models/file_model.py module."""
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

        self.file_info_1 = {
            "user_id":              1,
            "name":                 "test_name_1",
            "directory":            "test_directory_1",
            "compilation_options":  ["option1", "option2", "option3"],
            "language":             "test_language_1",
            "status":               "test_status_1",
        }

        self.file_info_2 = {
            "user_id":              2,
            "name":                 "test_name_2",
            "directory":            "test_directory_2",
            "compilation_options":  ["option1", "option2", "option3"],
            "language":             "test_language_2",
            "status":               "test_status_2",
        }

        self.test_user_1 = user_model.User(**self.user_info_1)
        self.test_user_1.id = self.user_info_1["id"] = 1
        self.test_user_2 = user_model.User(**self.user_info_2)
        self.test_user_2.id = self.user_info_2["id"] = 2

        self.test_file_1 = file_model.SourceCodeFile(**self.file_info_1)
        self.test_file_2 = file_model.SourceCodeFile(**self.file_info_2)

        self.test_user_1.create()
        self.test_user_2.create()
        self.test_file_1.create()
        self.test_file_2.create()

    def tearDown(self):
        self.test_file_1.delete()
        self.test_file_2.delete()
        self.test_user_1.delete()
        self.test_user_2.delete()

    def test_file_primary_key_auto_increment(self):
        db_file_1 = file_model.SourceCodeFile.get_files_per_language_by_user_id(self.file_info_1["user_id"])[0][1][0]
        db_file_2 = file_model.SourceCodeFile.get_files_per_language_by_user_id(self.file_info_2["user_id"])[0][1][0]

        self.assertEqual(abs(db_file_1["id"] - db_file_2["id"]), 1)
