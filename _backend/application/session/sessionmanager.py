import hashlib
import base64
import json
import aiohttp

from _backend.application.utils.publicappexception import PublicAppException


class SessionManager:
    def __init__(self):
        self.credentialLocation = "C:/Users/FSX-P/IdeaProjects/iRacing_DiscordBot/_backend/application/session/files/credentials.json"
        self.cookiejarLocation = "C:/Users/FSX-P/IdeaProjects/iRacing_DiscordBot/_backend/application/session/files/cookie-jar.txt"
        self.credentials = self.getCredentials()
        self.cookie_jar = aiohttp.CookieJar()
        self.session = None

    def getCredentials(self):
        return json.load(open(self.credentialLocation))

    def encode_pw(self):
        username = self.credentials["email"]
        password = self.credentials["password"]
        initialHash = hashlib.sha256((password + username.lower()).encode('utf-8')).digest()
        hashInBase64 = base64.b64encode(initialHash).decode('utf-8')
        return hashInBase64

    def newSession(self):
        self.session = aiohttp.ClientSession(cookie_jar=self.cookie_jar)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # if self.session and not self.session.closed:
        #     await self.session.close()
        return self

    async def authenticate(self):
        loginAdress = "https://members-ng.iracing.com/auth"
        loginHeaders = {"Content-Type": "application/json"}
        authBody = {"email": self.credentials["email"], "password": self.encode_pw()}

        await self.login(loginAdress, authBody, loginHeaders)

    async def login(self, loginAdress, authBody, loginHeaders):
        session = aiohttp.ClientSession(cookie_jar=self.cookie_jar)
        async with session as s:
            async with s.post(loginAdress, json=authBody, headers=loginHeaders) as response:
                if not response.status == 200:
                    raise Exception(f"[Sessionbuilder] API call unsuccessful, status code is {response.status}")
                else:
                    print("[Sessionbuilder] Authenticated")

def handleServerException(response, json):
    if response.status != 200:
        if response.status == 404:
            if json["message"]:
                message = json["message"]
            else:
                message = json
            raise PublicAppException(message)
        else:
            raise PublicAppException("iRacing API couldnt be reached. There may be maintenance work taking place at the moment.")