# Copyright (c) 2014 Mark Samman <https://github.com/marksamman/pylinkshortener>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import random
from datetime import datetime
from sqlalchemy import create_engine, Column, DateTime, ForeignKey, Integer, String, VARCHAR
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker
from app.constants import url_safe
import config

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    url = Column(VARCHAR)
    creator_ip = Column(CIDR)
    created = Column(DateTime)
    random = Column(String(2))

    def __init__(self, url, creator_ip):
        self.url = url
        self.created = datetime.utcnow()
        self.creator_ip = creator_ip
        self.random = ''.join(random.choice(url_safe) for _ in range(Link.random.property.columns[0].type.length))

    def __repr__(self):
        return '<Link %r>' % self.url

class Click(Base):
    __tablename__ = 'clicks'

    id = Column(Integer, primary_key=True)
    inserted = Column(DateTime)
    ip = Column(CIDR)
    user_agent = Column(VARCHAR)

    link_id = Column(Integer, ForeignKey('links.id'))
    link = relationship('Link', backref=backref('clicks', order_by=inserted.desc()))

    def __init__(self, ip, user_agent, inserted, link_id):
        self.inserted = inserted
        self.ip = ip
        self.user_agent = user_agent
        self.link_id = link_id

    def __repr__(self):
        return '<Click %r>' % self.inserted
