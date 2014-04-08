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
decode_array = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 35, -1, -1, 13, 49, 0, 56, 3, 62, 26, 63, 59, 11, -1, -1, -1, -1, -1, -1, -1, 43, 37, 54, 2, 32, 39, 33, 16, 4, 30, 40, 57, 31, 51, 15, 61, 20, 55, 29, 36, 45, 38, 17, 7, 28, 24, -1, -1, -1, -1, 44, -1, 6, 27, 25, 50, 10, 1, 9, 19, 12, 47, 22, 34, 52, 42, 5, 8, 58, 21, 18, 46, 53, 41, 48, 14, 23, 60]

def encode_int(i):
    if i == 0:
        return ''

    return encode_int(i >> 6) + url_safe[i & 63]

def decode_int(v):
    res = 0
    mult = 1
    for c in reversed(v):
        idx = ord(c)
        if idx >= len(decode_array):
            return 0

        val = decode_array[idx]
        if val == -1:
            return 0

        res += val * mult
        mult <<= 6
    return res

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.VARCHAR)
    creator_ip = db.Column(CIDR)
    created = db.Column(db.DateTime)
    clicks = db.Column(db.Integer, default=0)
    random = db.Column(db.String(2))

    def __init__(self, url, creator_ip):
        self.url = url
        self.created = datetime.utcnow()
        self.creator_ip = creator_ip
        self.random = ''.join(random.choice(url_safe) for _ in range(2))

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
    return redirect(url_for('shortened', link_id=encode_int(link.id)+link.random))

@app.route('/shortened/<string:link_id>')
def shortened(link_id):
    if len(link_id) < 3:
        abort(404)

    id = decode_int(link_id[:-2])
    if id == 0:
        abort(404)

    link = Link.query.filter_by(id=id).first()
    if link is None or link.random != link_id[-2:]:
        return render_template('index.html', error='There is no shortened link with that id.')
    elif ipaddress.ip_address(request.remote_addr) not in ipaddress.ip_network(link.creator_ip):
        return render_template('index.html', error='That shortened link was not generated from your network.')

    return render_template('shortened.html', base_url=request.host_url, encoded_id=encode_int(link.id), link=link)

@app.route("/<string:link_id>")
def visit_short_link(link_id):
    if len(link_id) < 3:
        abort(404)

    id = decode_int(link_id[:-2])
    if id == 0:
        abort(404)

    link = Link.query.filter_by(id=id).first()
    if link is None or link.random != link_id[-2:]:
        return render_template('index.html', error='There is no shortened link with that URL.')

    link.clicks += 1
    db.session.commit()
    return redirect(link.url)

if __name__ == "__main__":
    app.run(debug=True)
