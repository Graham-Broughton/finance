import json

import websocket

"""
Respond to the opening of a websocket connection.

Args:
    ws: write your description
"""
def on_open(ws):


socket = 'wss://api.ibkr.com/v1/api/ws'

ws = websocket.WebSocketApp(socket, on_open=on_open
