import datetime
import hashlib
import base64
import json
import os
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

    async def __aenter__(self):
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session and not self.session.closed:
            await self.session.close()

    def session(self):
        if self.session is None or self.session.closed:
            raise RuntimeError("Session not initialized")
        return self.session

    #todo: do only 1 time during start up process and just access cookie from cookie_jar
    async def authenticate(self):
        loginAdress = "https://members-ng.iracing.com/auth"
        loginHeaders = {"Content-Type": "application/json"}
        authBody = {"email": self.credentials["email"], "password": self.encode_pw()}

        cookieExists = os.path.exists(self.cookiejarLocation)

        if cookieExists:
            self.loadCookies(self.cookie_jar, self.cookiejarLocation)

            if self.isCookieJarValid(self.cookie_jar):
                session = aiohttp.ClientSession(cookie_jar=self.cookie_jar)
            else:
                session = aiohttp.ClientSession(cookie_jar=self.cookie_jar)
                response = await self.login(loginAdress, authBody, loginHeaders, session)
                if response["authcode"]:
                    self.saveCookies(self.cookie_jar, self.cookiejarLocation)
                else: raise Exception("No authcode received from enpoint while requesting access")

        else:
            session = aiohttp.ClientSession(cookie_jar=self.cookie_jar)
            response = await self.login(loginAdress, authBody, loginHeaders, session)
            if response["authcode"]:
                self.saveCookies(self.cookie_jar, self.cookiejarLocation)
            else: raise Exception("No authcode received from enpoint while requesting access")

        self.session = session

    def saveCookies(self, cookiejar, filename):
        cookiejar.save(filename)
        print("[Sessionbuilder] Cookies saved")

    async def login(self, loginAdress, authBody, loginHeaders, session):
        print("[Sessionbuilder] No valid cookie found: Authenticating with credentials")
        async with session as s:
            async with s.post(loginAdress, json=authBody, headers=loginHeaders) as response:
                if not response.status == 200:
                    raise Exception(f"[Sessionbuilder] API call unsuccessful, status code is {response.status}")
                else:
                    print("[Sessionbuilder] Authenticated")
                    return await response.json()

    def loadCookies(self, cookiejar, filename):
        return cookiejar.load(filename)

    def isCookieJarValid(self, cookie_jar):

        invalid = False

        for cookie in cookie_jar:
            date_str = cookie["expires"]
            date_cookie = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=datetime.timezone.utc)
            date_now = datetime.datetime.now(datetime.timezone.utc)

            if date_now > date_cookie:
                invalid = True

        return not invalid

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