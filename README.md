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
$ python linkshortener.py
```

### TODO
* Only allow shortening URL to links that return HTTP status code 200 (OK)
* Store clicks in separate table with more information (timestamp, ip, browser)
* Show clicks in realtime in /shortened/id
* Cache popular links with Redis
* Graphs of click data
* JSON API
