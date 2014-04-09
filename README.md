pylinkshortener
===============

Link shortener written in Python using Flask, PostgreSQL and SQLAlchemy

### Setup
#### Installation
Installing the required modules:
```bash
$ pip install -r requirements.txt
```

#### Configuration
Configure SQLALCHEMY_DATABASE_URI in linkshortener.py and then run this in the Python interpreter to setup the database tables:
```py
from linkshortener import db
db.create_all()
```

#### Run:
```bash
$ python run.py
```

### TODO
* Only allow shortening URL to links that return HTTP status code 200 (OK)
* Show clicks in realtime in /shortened/id
* Non-blocking insert click & realtime socket send when visiting short URL
* Cache popular links with Redis
* Graphs of click data
* JSON API
