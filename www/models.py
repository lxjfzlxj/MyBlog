import time
from ORM import BooleanField, FloatField, Model, StringField, TextField
import uuid

def newID():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'
    
    id = StringField(column_type = 'varchar(50)', primary_key = True, default = newID)
    username = StringField(column_type = 'varchar(50)')
    password = StringField(column_type = 'varchar(50)')
    admin = BooleanField()
    email = StringField(column_type = 'varchar(50)')
    image = StringField(column_type = 'varchar(500)')
    create_time = FloatField(default = time.time)


class Blog(Model):
    __table__ = 'blogs'
    
    id = StringField(column_type = 'varchar(50)', primary_key = True, default = newID)
    userid = StringField(column_type = 'varchar(50)')
    username = StringField(column_type = 'varchar(50)')
    userimage = StringField(column_type = 'varchar(500)')
    title = StringField(column_type = 'varchar(50)')
    content = TextField()
    create_time = FloatField(default = time.time)
  

class Comment(Model):
    __table__ = 'comments'
    id = StringField(column_type = 'varchar(50)', primary_key = True, default = newID)
    blogid = StringField(column_type = 'varchar(50)')
    userid = StringField(column_type = 'varchar(50)')
    username = StringField(column_type = 'varchar(50)')
    userimage = StringField(column_type = 'varchar(500)')
    content = TextField()
    create_time = FloatField(default = time.time)