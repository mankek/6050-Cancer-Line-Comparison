import unittest
from Interface import GDCQuery


class TestGDC(unittest.TestCase):
    def setUp(self):
        # this tissue provides max number of files
        self.normal_organ = GDCQuery("Brain")
        # this tissue provides no files
        self.no_file_organ = GDCQuery("Nasopharynx")
        # no tissue
        self.no_organ = GDCQuery("")
        # invalid formatting
        self.bad_format = GDCQuery(True)

    def test_parameters(self):
        # good tissue
        param_result_norm = self.normal_organ.param_construct()
        self.assertIsInstance(param_result_norm, dict)
        # no files
        param_result_no_file = self.no_file_organ.param_construct()
        self.assertIsInstance(param_result_no_file, dict)
        # no tissue
        param_result_no = self.no_organ.param_construct()
        self.assertIsInstance(param_result_no, dict)
        # bad formatting (not caught here)
        param_result_bad = self.bad_format.param_construct()
        self.assertIsInstance(param_result_bad, dict)

    def test_query_files(self):
        # good tissue
        norm_resp, norm_list = self.normal_organ.query_files()
        self.assertEqual(len(norm_list), 20)
        self.assertEqual(norm_resp.status_code, 200)
        # no files
        no_resp, no_list = self.no_organ.query_files()
        self.assertEqual(len(no_list), 0)
        self.assertEqual(no_resp.status_code, 200)
        # no tissue (not caught here)
        no_file_resp, no_file_list = self.no_file_organ.query_files()
        self.assertEqual(len(no_file_list), 0)
        self.assertEqual(no_file_resp.status_code, 200)
        # bad formatting (not caught here)
        bad_resp, bad_list = self.bad_format.query_files()
        self.assertEqual(len(bad_list), 0)
        self.assertEqual(bad_resp.status_code, 200)

    def test_query_data(self):
        self.normal_organ.query_files()
        # normal number of files
        text_resp = self.normal_organ.query_data(5)
        self.assertEqual(text_resp, "Data from 5 files has been parsed!\n")
        # more files than available
        too_many = self.normal_organ.query_data(100)
        self.assertEqual(too_many, "Data from 15 files has been parsed!\n")
        # no files available
        self.no_file_organ.query_files()
        text_resp = self.no_file_organ.query_data(5)
        self.assertEqual(text_resp, "No data available!\n")
        # not a tissue
        self.no_organ.query_files()
        text_resp = self.no_organ.query_data(5)
        self.assertEqual(text_resp, "No data available!\n")
        # bad formatting
        self.bad_format.query_files()
        text_resp = self.bad_format.query_data(5)
        self.assertEqual(text_resp, "No data available!\n")
        # bad file IDs
        self.normal_organ.file_uuid_list = ["testtestest"]
        text_resp = self.normal_organ.query_data(5)
        self.assertEqual(text_resp, "Data from 0 files has been parsed!\n")

    # def test_parse_data(self):
    #     self.no_file_organ

    def test_read_data(self):
        bad_path = r"None\test"
        filename = "test.counts"
        with self.assertRaises(FileNotFoundError):
            self.normal_organ.read_data(bad_path, filename)


if __name__ == '__main__':
    unittest.main()
