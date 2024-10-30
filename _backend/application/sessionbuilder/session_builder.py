import hashlib
import base64
import json
import os
import requests
from http.cookiejar import LWPCookieJar


class SessionBuilder:
    def __init__(self):
        self.session = None
        self.credentials = self.getCredentials()

    def getCredentials(self):
        return json.load(
            open(
                "C:/Users/FSX-P/IdeaProjects/iRacing_WebApp/_backend/application/sessionbuilder/files/credentials.json"))

    def encode_pw(self):
        username = self.credentials["email"]
        password = self.credentials["password"]
        initialHash = hashlib.sha256((password + username.lower()).encode('utf-8')).digest()
        hashInBase64 = base64.b64encode(initialHash).decode('utf-8')
        return hashInBase64

    def authenticate(self):
        loginAdress = "https://members-ng.iracing.com/auth"
        loginHeaders = {"Content-Type": "application/json"}

        authBody = {"email": self.credentials["email"], "password": self.encode_pw()}

        self.session = requests.Session()
        cookie_File = "C:/Users/FSX-P/IdeaProjects/iRacing_WebApp/_backend/application/sessionbuilder/files/cookie-jar.txt"
        self.session.cookies = LWPCookieJar(cookie_File)

        if os.path.exists(cookie_File):
            self.session.cookies.load(cookie_File)

        responseStatusCode = self.session.get('https://members-ng.iracing.com/data/car/get').status_code

        if responseStatusCode == 401:
            print('[session_builder] setting cookies')
            self.session.cookies.save()
            loginNow = self.session.post(loginAdress, json=authBody, headers=loginHeaders)
            response_Data = loginNow.json()

            if loginNow.status_code == 200 and response_Data['authcode']:
                if cookie_File:
                    self.session.cookies.save(ignore_discard=True)
            else:
                raise RuntimeError("Error from iRacing: ", response_Data)
        else:
            print('[session_builder] loading saved cookies')
            self.session.cookies.load(cookie_File)


def responseIsValid(response):
    return response.status_code == 200
