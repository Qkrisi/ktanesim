from json import dumps

class User:
    def __init__(self, username, discriminator, id, **kwargs):
        self.id = id
        self.username = username
        self.discriminator = discriminator
        self.tag = f"{username}#{discriminator}"
        self.mention = f"<@{id}>"

    def __str__(self):
        return self.tag

class Channel:
    def __init__(self, socket, id, **kwargs):
        self.socket = socket
        self.id = id
    
    def __str__(self):
        return str(self.id)

    async def send(self, msg, file=None, embed=None):
        await self.socket.send(dumps({"id":self.id, "message":msg, "file":file, "embed":embed}))

class Message:
    def __init__(self, author, channel, id, content, **kwargs):
        self.author = author
        self.channel = channel
        self.id = id
        self.content = content
