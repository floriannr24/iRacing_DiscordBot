import sqlite3
import json

location = "../database/bot.db"

def getMemberIdForDiscordId(discordId):
    con = sqlite3.connect(location)
    cur = con.cursor()

    params = (discordId, )
    cur.execute("SELECT custId FROM members WHERE discordId = ?", params)
    result = cur.fetchone()
    return result[0] if result else None

def storeNewMemberId(custId, discordId):
    con = sqlite3.connect(location)
    cur = con.cursor()

    params = (custId, discordId)
    cur.execute("INSERT INTO members (custId, discordId) VALUES (?, ?)", params)

    con.commit()

def updateMemberId(custId, discordId):
    con = sqlite3.connect(location)
    cur = con.cursor()

    params = (custId, discordId)
    cur.execute("UPDATE members SET custId = ? WHERE discordId = ?", params)

    con.commit()

def getSessionForUser(custId, sessionId):
    con = sqlite3.connect(location)
    cur = con.cursor()

    params = (custId, sessionId)
    cur.execute("SELECT data FROM sessions WHERE custId = ? and sessionId = ? ", params)

    result = cur.fetchone()
    return json.loads(result[0]) if result else None

def storeSessionForUser(custId, sessionId, data):
    con = sqlite3.connect(location)
    cur = con.cursor()

    jsonData = json.dumps(data)

    params = (custId, sessionId, jsonData)
    cur.execute("INSERT INTO sessions (custId, sessionId, data) VALUES (?, ?, ?)", params)

    con.commit()