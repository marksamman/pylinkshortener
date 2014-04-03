#!/usr/bin/env python3
#
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

import ipaddress, random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, abort
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import CIDR

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mark@localhost/linkshortener'
db = SQLAlchemy(app)

url_safe = ('2', 'f', 'D', '4', 'I', 'o', 'a', 'X', 'p', 'g', 'e', '9', 'i', '0', 'x', 'O', 'H', 'W', 's', 'h', 'Q', 'r', 'k', 'y', 'Z', 'c', '6', 'b', 'Y', 'S', 'J', 'M', 'E', 'G', 'l', '-', 'T', 'B', 'V', 'F', 'K', 'v', 'n', 'A', '_', 'U', 't', 'j', 'w', '1', 'd', 'N', 'm', 'u', 'C', 'R', '3', 'L', 'q', '8', 'z', 'P', '5', '7')

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.VARCHAR)
    creator_ip = db.Column(CIDR)
    created = db.Column(db.DateTime)
    clicks = db.Column(db.Integer, default=0)
    random = db.Column(db.String(4))

    def __init__(self, url, creator_ip):
        self.url = url
        self.created = datetime.utcnow()
        self.creator_ip = creator_ip
        self.random = ''.join(url_safe[random.randint(0, len(url_safe)-1)] for _ in range(4))

    def __repr__(self):
        return '<Link %r>' % self.url

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/shorten", methods=['POST'])
def shorten():
    link = Link(request.form['url'], request.remote_addr)
    db.session.add(link)
    db.session.commit()
    return redirect(url_for('shortened', link_id=link.id))

@app.route('/shortened/<int:link_id>')
def shortened(link_id):
    link = Link.query.filter_by(id=link_id).first()
    if link is None:
        return render_template('index.html', error='There is no shortened link with that id.')

    if ipaddress.ip_address(request.remote_addr) not in ipaddress.ip_network(link.creator_ip):
        return render_template('index.html', error='That shortened link was not generated from your network.')

    return render_template('shortened.html', base_url=request.host_url, link=link)

@app.route("/<string:link_id>")
def visit_short_link(link_id):
    if len(link_id) < 5:
        abort(404)

    try:
        id = int(link_id[:-4])
    except ValueError:
        abort(404)

    link = Link.query.filter_by(id=id).first()
    if link is None or link.random != link_id[-4:]:
        return render_template('index.html', error='There is no shortened link with that URL.')

    link.clicks += 1
    db.session.commit()
    return redirect(link.url)

if __name__ == "__main__":
    app.run(debug=True)
