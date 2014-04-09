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
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import CIDR
from app.constants import url_safe

db = SQLAlchemy()

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.VARCHAR)
    creator_ip = db.Column(CIDR)
    created = db.Column(db.DateTime)
    random = db.Column(db.String(2))

    def __init__(self, url, creator_ip):
        self.url = url
        self.created = datetime.utcnow()
        self.creator_ip = creator_ip
        self.random = ''.join(random.choice(url_safe) for _ in range(Link.random.property.columns[0].type.length))

    def __repr__(self):
        return '<Link %r>' % self.url

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inserted = db.Column(db.DateTime)
    ip = db.Column(CIDR)
    user_agent = db.Column(db.VARCHAR)

    link_id = db.Column(db.Integer, db.ForeignKey('link.id'))
    link = db.relationship('Link', backref=db.backref('clicks', lazy='dynamic'))

    def __init__(self, ip, user_agent, link):
        self.inserted = datetime.utcnow()
        self.ip = ip
        self.user_agent = user_agent
        self.link = link

    def __repr__(self):
        return '<Click %r>' % self.inserted
