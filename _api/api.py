import sqlite3
from _api.apiMock import read_file_content
from _backend.application.dataprocessors.boxplot import Boxplot
from _backend.application.diagrams.boxplot import BoxplotDiagram

location = "../_api/bot.db"
# location = "bot.db"


async def getBoxplotData(**kwargs):

    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)

    userId = 817394
    selectedSession = -1
    # subsessionId = 50881221

    responseData = await Boxplot().get_Boxplot_Data(userId=userId, selectedSession=selectedSession, subsessionId=subsessionId)

    # write_file_content(responseData)
    # responseData = read_file_content()

    fileLocation = BoxplotDiagram(responseData, showRealName=showRealName).draw()

    return fileLocation

def createDatabase():
    conn = sqlite3.connect(location)
    cur = conn.cursor()
    cur.execute('''DROP TABLE IF EXISTS members ''')
    cur.execute('''
        CREATE TABLE members (
            custId INTEGER, 
            discordId INTEGER,
            active INTEGER, 
            PRIMARY KEY (custId, discordId)
            )
    ''')

def getActiveMemberIdForDiscordId(discordId):
    con = sqlite3.connect(location)
    cur = con.cursor()

    params = (discordId, )
    cur.execute("SELECT custId FROM members WHERE discordId = ? AND active = 1", params)
    result = cur.fetchone()
    return result[0] if result else None

def storeNewCustIdInDatabase(custId, discordId):
    con = sqlite3.connect(location)
    cur = con.cursor()

    params1 = (discordId, ) # reset all active-flags for discordId
    cur.execute("UPDATE members SET active = 0 WHERE discordId = ?", params1)

    params2 = (custId, discordId, 1) # 1 = set as active combination
    cur.execute("INSERT INTO members (custId, discordId, active) VALUES (?, ?, ?)", params2)

    con.commit()

def updateActiveCombination(custId, discordId):
    con = sqlite3.connect(location)
    cur = con.cursor()

    params1 = (discordId, )
    cur.execute("UPDATE members SET active = 0 WHERE discordId = ?", params1)

    params2 = (discordId, custId, )
    cur.execute("UPDATE members SET active = 1 WHERE discordId = ? AND custId = ?", params2)

    con.commit()

def entryForMemberIdExists(custId, discordId):
    con = sqlite3.connect(location)
    cur = con.cursor()

    params = (discordId, custId)
    cur.execute("SELECT custId FROM members WHERE discordId = ? AND custId = ?", params)
    result = cur.fetchone()
    return True if result else False

def getAllEntries():
    con = sqlite3.connect(location)
    cur = con.cursor()

    cur.execute("SELECT * FROM members")
    result = cur.fetchall()
    print(result)

# createDatabase()

# res = getActiveMemberIdForDiscordId(894719931193634877)
# print(res)

# storeNewCustIdInDatabase(123, 894719931193634877)

getAllEntries()










