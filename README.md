pylinkshortener
===============

Link shortener written in Python using Flask, PostgreSQL, SQLAlchemy and WebSocket (using asyncio). pylinkshortener requires Python 3.4 or newer.

### Setup
#### Installation
Installing the required modules:
```bash
$ pip install -r requirements.txt
```

#### Configuration
Configure SQLALCHEMY_DATABASE_URI in config.py and then run this in the Python interpreter to setup the database tables:
```py
from app.models import Base, engine
Base.metadata.create_all(engine)
```

#### Run:
```bash
$ python run.py
```

### TODO
* Only allow shortening URL to links that return HTTP status code 200 (OK)
* Graphs of click data
* JSON API
