from DiscordModels import *
from json import loads
import asyncio
import websockets
import config


host = config.HOST
port = config.PORT

def OnMessage(func):
    global Func_OnMessage
    Func_OnMessage = func
    return func

ChannelCache = {}

async def HandleSocket(websocket, path):
    print("Main bot connected")
    while True:
        try:data = loads(await websocket.recv())
        except Exception as e:
            print(f"Error: {str(e)}")
            return
        data["channel"]["socket"]=websocket
        ChannelID = data["channel"]["id"]
        channel = ChannelCache[ChannelID] if ChannelID in ChannelCache else Channel(**data["channel"])
        channel.socket = websocket
        ChannelCache[ChannelID]=channel
        await Func_OnMessage(Message(User(**data["author"]), channel, **data["message"]))


def Start():
    print(f"Running on port {port}")
    asyncio.get_event_loop().run_until_complete(websockets.serve(HandleSocket, host, port))
    asyncio.get_event_loop().run_forever()

if __name__=="__main__":Start()
