import json

import websocket

def on_open(ws):


socket = 'wss://api.ibkr.com/v1/api/ws'

ws = websocket.WebSocketApp(socket, on_open=on_open
