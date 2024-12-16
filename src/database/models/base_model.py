import peewee as pw
from peewee import DateTimeField
from utils import PATH
import datetime

DB_PARAMS = dict(
    foreign_keys=1
)

DB = pw.SqliteDatabase(PATH.DATABASE_FILE, pragmas=DB_PARAMS)


class BaseModel(pw.Model):
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB
