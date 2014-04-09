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

import ipaddress
from flask import Flask, render_template, request, redirect, url_for, abort
from app.util import encode_int, decode_int
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app.models import Link, Click

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

	db.session.add(Click(request.remote_addr, request.headers.get('User-Agent'), link))
	db.session.commit()
	return redirect(link.url)
