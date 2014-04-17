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

import asyncio, ipaddress, json, queue, websockets
from app import clicksQueue
from app.models import Session, Link, Click

wsClients = dict()
asyncio_session = Session()

@asyncio.coroutine
def handleClicks():
	while True:
		# FIXME: should yield from queue.get with asyncio.Queue
		# but we can't put in asyncio.Queue from Flask thread
		try:
			queuedClick = clicksQueue.get(False)
		except queue.Empty:
			yield from asyncio.sleep(0.25)
			continue

		click = Click(queuedClick.ip, queuedClick.user_agent, None)
		click.link_id = queuedClick.link_id

		asyncio_session.add(click)
		asyncio_session.commit()

		json_data = json.dumps({
			"inserted": queuedClick.inserted.strftime("%c"),
			"ua": queuedClick.user_agent
		})

		if click.link_id in wsClients:
			for client in wsClients[click.link_id]:
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

	link = asyncio_session.query(Link).filter_by(id=link_id).first()
	if link is None:
		return

	remote_addr = websocket.writer.get_extra_info("peername")[0]
	if ipaddress.ip_address(remote_addr) not in ipaddress.ip_network(link.creator_ip):
		return

	if link_id not in wsClients:
		wsClients[link_id] = set()

	wsClients[link_id].add(websocket)
	yield from websocket.recv()
	wsClients[link_id].remove(websocket)

def websocketThread():
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	asyncio.Task(handleClicks())
	asyncio.Task(websockets.serve(handleConnection, 'localhost', 5001))
	loop.run_forever()
