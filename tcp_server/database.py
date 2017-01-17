import MySQLdb


def connect_db():
    """Connects to the specific database."""
    db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="test")
    db.autocommit(True)
    return db


def get_db():
    mysql_db = connect_db()
    return mysql_db


def save_data(command, data):
    db = get_db()
    db.cursor().execute(command, data)
    db.commit()
    db.cursor().close()
    db.close()
