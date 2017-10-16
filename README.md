Flask-PicoCMS
=============

Lightweight CMS backend for Flask apps.

Installation
------------
The easiest way to install this is through pip.
```
pip install Flask-PicoCMS
```

Basic example
-------------
Flask code `app.py`

```python
import os
from flask import Flask
from flask_picocms import CMS


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["PICOCMS_DATABASE"] = os.path.join(basedir, "cms.sqlite")
app.config["PICOCMS_SOURCE_PAGES"] = os.path.join(basedir, "cms", "pages")
app.config["PICOCMS_SOURCE_DATA"] = os.path.join(basedir, "cms", "data")

pico = CMS(app)


# to make development easier
@app.before_request
def rebuild_cms():
    pico.rebuild()

@app.route("/")
def index():
    page = pico.get_content("/welcome")
    return page.json["content"]["message"]
```

CMS file (*.toml* or *.json*) `cms/pages/welcome.toml`

```toml
title="welcome"
draft=false
date="2017-10-15"

[content]
title="welcome to picocms"
message="Hello World!"
```