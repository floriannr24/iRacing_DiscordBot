import os
import sqlite3
import json

class apiDatabase:
    def __init__(self):
        self.location = "./database/bot.db"
        self._BOXED = os.environ.get("BOXED", False) == "True"
        self._DISABLE_CACHING_SESSION = os.environ.get("DISABLE_CACHING_SESSION", False) == "True"

    def getMemberIdForDiscordId(self, discordId):

        con = sqlite3.connect(self.location)
        cur = con.cursor()

        params = (discordId, )
        cur.execute("SELECT custId FROM members WHERE discordId = ?", params)
        result = cur.fetchone()
        return result[0] if result else None

    def storeNewMemberId(self, custId, discordId) -> None:

        con = sqlite3.connect(self.location)
        cur = con.cursor()

        params = (custId, discordId)
        cur.execute("INSERT INTO members (custId, discordId) VALUES (?, ?)", params)

        con.commit()

    def updateMemberId(self, custId, discordId) -> None:

        con = sqlite3.connect(self.location)
        cur = con.cursor()

        params = (custId, discordId)
        cur.execute("UPDATE members SET custId = ? WHERE discordId = ?", params)

        con.commit()

    def deleteMember(self, discordId):
        con = sqlite3.connect(self.location)
        cur = con.cursor()

        params = (discordId, )
        cur.execute("DELETE FROM members WHERE discordId = ?", params)

        con.commit()

    def getSessionDataForUser(self, custId, sessionId):

        if not self._DISABLE_CACHING_SESSION:

            con = sqlite3.connect(self.location)
            cur = con.cursor()

            params = (custId, sessionId)
            cur.execute("SELECT data FROM sessions WHERE custId = ? and sessionId = ? ", params)

            result = cur.fetchone()
            return json.loads(result[0]) if result else None

        else:
            return None

    def storeSessionDataForUser(self, custId, sessionId, data) -> None:

        if not self._DISABLE_CACHING_SESSION:

            con = sqlite3.connect(self.location)
            cur = con.cursor()

            jsonData = json.dumps(data)

            params = (custId, sessionId, jsonData)
            cur.execute("INSERT INTO sessions (custId, sessionId, data) VALUES (?, ?, ?)", params)

            con.commit()

        else:
            return None