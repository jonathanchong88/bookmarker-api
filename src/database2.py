from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

import string
import random
db = SQLAlchemy()
ma = Marshmallow()


class Person(db.Model):
    person_id = db.Column(UUID(as_uuid=True), primary_key=True,
                          nullable=False, default=uuid.uuid4)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    updated_date = db.Column(db.DateTime, default=datetime.now())
    date_of_birth = db.Column(db.DATE)

    def __repr__(self) -> str:
        return 'User>>> {self.email}'


# create Person schema
class PersonSchema(ma.Schema):
    class Meta:
        fields = ['first_name','last_name','nickname','status','email', 'created_date',]


# create instance of schema
person_schema = PersonSchema(many=False)
persons_schema = PersonSchema(many=True)

