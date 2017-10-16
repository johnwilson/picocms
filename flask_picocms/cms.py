import os
import shutil
import toml
import json
from datetime import datetime
from flask import current_app
from peewee import *

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


database = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = database


class Page(BaseModel):
    """Model for CMS page contents: converted from TOML to JSON"""
    title = CharField(default="")
    directory = CharField(default="/")
    name = CharField(null=False)
    date = DateTimeField(default=datetime.utcnow)
    draft = BooleanField(default=True)
    content = TextField(default="")

    class Meta:
        indexes = (
            (("directory","name"), True),
        )


class Document(BaseModel):
    """Model for CMS JSON documents"""
    directory = CharField(default="/")
    name = CharField(null=False)
    content = TextField()

    class Meta:
        indexes = (
            (("directory","name"), True),
        )


class CMS(object):
    """Lytpages CMS"""
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, "teardown_appcontext"):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)        

        database.init(app.config["PICOCMS_DATABASE"])
        database.connect()

    def teardown(self, exception):
        database.close()
        
    def rebuild(self):
        self.clear()
        self.parse()

    def clear(self):
        database.drop_tables([Page, Document], safe=True)
        database.create_tables([Page, Document])
    
    def parse(self):
        self.__add_content()
        self.__add_data()

    def get_content(self, path):        
        directory = os.path.dirname(path)
        name = os.path.basename(path)

        try:
            page = Page.get(
                Page.directory == directory,
                Page.name == name
            )
        except Page.DoesNotExist:
            raise ValueError("Invalid Content path: %s" % path)
        
        return page

    @property
    def content_count(self):
        return Page.select().count()

    def list_content(self, directory, date="asc"):
        res = []

        if date == "desc":
            orderby = Page.date.desc()
        else:
            orderby = Page.date.asc()

        for item in Page.select().where(Page.directory == directory).order_by(orderby):
            medata = {
                "title": item.title,
                "directory": item.directory,
                "name": item.name,
                "date": item.date,
                "draft": item.draft
            }
            res.append(medata)

        return res

    def get_data(self, path):
        directory = os.path.dirname(path)
        name = os.path.basename(path)

        try:
            doc = Document.get(
                Document.directory == directory,
                Document.name == name
            )
        except Document.DoesNotExist:
            raise ValueError("Invalid Data path: %s" % path)
        
        return doc

    @property
    def data_count(self):
        return Document.select().count()

    def __add_content(self):
        _dir = self.app.config["PICOCMS_SOURCE_PAGES"]
        
        for root, dirs, files in os.walk(_dir):
            for item in files:
                name, directory, data, data_str = self.__get_file_data(_dir, item, root)
                
                # create repository entry
                pg = Page(content=data_str, directory=directory, name=name)
                if "title" in data:
                    pg.title = data["title"]
                if "draft" in data:
                    pg.draft = data["draft"]
                if "date" in data:
                    pg.date = data["date"]                
                pg.save()

    def __add_data(self):
        _dir = self.app.config["PICOCMS_SOURCE_DATA"]
        
        for root, dirs, files in os.walk(_dir):
            for item in files:
                name, directory, data, data_str = self.__get_file_data(_dir, item, root)
                
                # create repository entry  
                doc = Document(content=data_str, directory=directory, name=name)
                doc.save()

    def __get_file_data(self, srcdir, fname, fdir):
        abspath = os.path.join(fdir, fname)
                
        # create repository indexing fields
        name, ext = os.path.splitext(fname)
        directory = fdir.replace(srcdir, "")
        if not directory:
            directory = "/"

        # get file contents and parse
        with open(abspath, "r") as fp:
            fraw = fp.read()

        if ext == ".toml":
            data = toml.loads(fraw)
            data_str = json.dumps(data)
        elif ext == ".json":
            data = json.loads(fraw)
            data_str = fraw

        return name, directory, data, data_str