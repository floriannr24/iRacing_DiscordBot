import hashlib
import base64
import json
from datetime import datetime

import aiohttp

from _backend.application.utils.publicappexception import PublicAppException


class SessionManager:
    def __init__(self):
        self.credentialLocation = "C:/Users/FSX-P/IdeaProjects/iRacing_DiscordBot/_backend/application/session/files/credentials.json"
        self.cookiejarLocation = "C:/Users/FSX-P/IdeaProjects/iRacing_DiscordBot/_backend/application/session/files/cookie-jar.txt"
        self.credentials = self.getCredentials()
        self.session = None

    def getCredentials(self):
        return json.load(open(self.credentialLocation))

    def encode_pw(self):
        username = self.credentials["email"]
        password = self.credentials["password"]
        initialHash = hashlib.sha256((password + username.lower()).encode('utf-8')).digest()
        hashInBase64 = base64.b64encode(initialHash).decode('utf-8')
        return hashInBase64

    def newSession(self, cookie):
        self.session = aiohttp.ClientSession(cookie_jar=cookie)

    async def authenticate(self) -> aiohttp.CookieJar:
        loginAdress = "https://members-ng.iracing.com/auth"
        loginHeaders = {"Content-Type": "application/json"}
        authBody = {"email": self.credentials["email"], "password": self.encode_pw()}

        return await self.login(loginAdress, authBody, loginHeaders)

    async def login(self, loginAdress, authBody, loginHeaders):
        cookie_jar = aiohttp.CookieJar()
        session = aiohttp.ClientSession(cookie_jar=cookie_jar)
        async with session as s:
            async with s.post(loginAdress, json=authBody, headers=loginHeaders) as response:
                if not response.status == 200:
                    raise Exception(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Authentication call unsuccessful, status code is {response.status}")
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Authenticated")
                    return cookie_jar


def getMessage404(json):
    if json["message"]:
        message = json["message"]
    else:
        message = json
    return message

def getMessage400(json):
    if json["message"]:
        message = json["message"]
    else:
        message = json
    return message

def checkForBadServerResponse(response, json):
    if response.status != 200:
        if response.status == 404:
            message = getMessage404(json)
            raise PublicAppException(message)
        if response.status == 400:
            message = getMessage400(json)
            raise PublicAppException(message)
        else:
            raise PublicAppException("iRacing API couldn't be reached. There may be maintenance work taking place at the moment.")
