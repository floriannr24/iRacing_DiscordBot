import hashlib
import base64
import json
import os
from datetime import datetime
from pathlib import Path

import aiohttp

from _backend.application.utils.publicappexception import PublicAppException

class SessionManager:
    def __init__(self):
        self._CREDENTIALS_EMAIL = os.environ.get("CREDENTIALS_EMAIL", None)
        self._CREDENTIALS_PASSWORD = os.environ.get("CREDENTIALS_PASSWORD", None)

        self.session = None

    def encode_pw(self, username, password):
        initialHash = hashlib.sha256((password + username.lower()).encode('utf-8')).digest()
        hashInBase64 = base64.b64encode(initialHash).decode('utf-8')
        return hashInBase64

    def newSession(self, cookie):
        self.session = aiohttp.ClientSession(cookie_jar=cookie)

    async def authenticateAndGetCookie(self) -> aiohttp.CookieJar:

        if self.credentialsLoaded():
            email = self._CREDENTIALS_EMAIL
            password = self._CREDENTIALS_PASSWORD

            loginAdress = "https://members-ng.iracing.com/auth"
            loginHeaders = {"Content-Type": "application/json"}

            authBody = {"email": email, "password": self.encode_pw(email, password)}

            cookie = await self.login(loginAdress, authBody, loginHeaders)
            return cookie
        else:
            raise Exception("No credentials found")

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

    def credentialsLoaded(self):
        return self._CREDENTIALS_EMAIL and self._CREDENTIALS_PASSWORD

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
