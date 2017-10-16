import unittest
import os
import shutil
import json
from flask import Flask
from flask_picocms import CMS

basedir = os.path.abspath(os.path.dirname(__file__))

class RepositoryCreationTestCase(unittest.TestCase):
    def setUp(self):
        self.dbname = "picocms-test.sqlite"

        app = Flask(__name__)
        app.config["PICOCMS_DATABASE"] = os.path.join(basedir, self.dbname)
        app.config["PICOCMS_SOURCE_PAGES"] = os.path.join(basedir, "sample", "pages")
        app.config["PICOCMS_SOURCE_DATA"] = os.path.join(basedir, "sample", "data")

        pico = CMS(app)

        self.app = app
        self.pico = pico

        self.pico.rebuild()        

    def tearDown(self):
        self.pico.teardown(None)
        if os.path.exists(self.app.config["PICOCMS_DATABASE"]):
            os.remove(self.app.config["PICOCMS_DATABASE"])
        
    def test_db_creation(self):
        self.assertTrue(os.path.exists(self.app.config["PICOCMS_DATABASE"]))

    def test_page_creation(self):
        self.assertEqual(self.pico.content_count, 3)

    def test_data_creation(self):
        self.assertEqual(self.pico.data_count, 1)

    def test_page_content(self):
        page = self.pico.get_content("/index")
        self.assertTrue(page.meta["draft"])
        self.assertEqual(page.meta["name"], "index")

    def test_doc_content(self):
        doc = self.pico.get_data("/site")
        self.assertEqual(doc.meta["name"], "site")

        self.assertEqual(doc.json["name"], "PicoCMS")

    def test_page_list(self):
        res = self.pico.list_content("/news")
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["title"], "news item 2")
