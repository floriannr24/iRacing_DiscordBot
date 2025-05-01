import sqlite3

location = "./bot_prod.db"


def createDatabase():
    conn = sqlite3.connect(location)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS members")
    cur.execute("DROP TABLE IF EXISTS sessions")

    cur.execute("CREATE TABLE members ("
                "custId INTEGER, "
                "discordId INTEGER PRIMARY KEY"
                ")")

    cur.execute("CREATE TABLE sessions ("
                "custId INTEGER, "
                "sessionId INTEGER, "
                "data TEXT, "
                "PRIMARY KEY (custId, sessionId)"
                ")")


if __name__ == "__main__":
    createDatabase()
