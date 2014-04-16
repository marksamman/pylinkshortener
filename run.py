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

import asyncio, ipaddress, json, psycopg2, queue, threading, websockets

from app import app, clicksQueue

clients = dict()

# FIXME: use SQLAlchemy
conn = psycopg2.connect("host='localhost' dbname='linkshortener' user='mark'")
cursor = conn.cursor()

@asyncio.coroutine
def handleClicks():
	while True:
		# FIXME: should yield from queue.get with asyncio.Queue
		# but we can't put in asyncio.Queue from Flask thread
		try:
			click = clicksQueue.get(False)
		except queue.Empty:
			yield from asyncio.sleep(0.25)
			continue

		cursor.execute("INSERT INTO click (inserted, ip, user_agent, link_id) VALUES (%s, %s, %s, %s)",
						(click.inserted, click.ip, click.user_agent, click.link_id))
		conn.commit()

		json_data = json.dumps({
			"inserted": click.inserted.strftime("%c"),
			"ua": click.user_agent
		})
		if click.link_id in clients:
			for client in clients[click.link_id]:
				yield from client.send(json_data)

@asyncio.coroutine
def handleConnection(websocket, uri):
	link_id = yield from websocket.recv()
	try:
		link_id = int(link_id)
	except ValueError:
		return

	if link_id == 0:
		return

	cursor.execute("SELECT creator_ip FROM link WHERE id = %s", (link_id,))
	res = cursor.fetchone()
	if res is None:
		return

	remote_addr = websocket.writer.get_extra_info("peername")[0]
	if ipaddress.ip_address(remote_addr) not in ipaddress.ip_network(res[0]):
		return

	if link_id not in clients:
		clients[link_id] = set()

	clients[link_id].add(websocket)
	yield from websocket.recv()
	clients[link_id].remove(websocket)

def asyncioThread():
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	asyncio.Task(handleClicks())
	asyncio.Task(websockets.serve(handleConnection, 'localhost', 5001))
	loop.run_forever()

if __name__ == "__main__":
	threading.Thread(target=asyncioThread).start()
	app.run()
