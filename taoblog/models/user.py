# -*- coding: utf-8 -*-

__all__ = ['User', 'UserOperator']

from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import validates
from . import Base, ModelError


class UserError(ModelError):
    def __init__(self, message):
        ModelError.__init__(self, message, model='User')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    # todo: provider and token must be unique
    provider = Column(String, nullable=False)
    identity = Column(String, nullable=False)

    def __init__(self, name, email, provider, identity):
        self.name = name
        self.email = email
        self.provider = provider
        self.identity = identity

    @validates('name')
    def validate_name(self, _, name):
        if not name.strip():
            raise UserError('empty name')
        if len(name) < 2:
            raise UserError('name too short')
        elif len(name) > 36:
            raise UserError('name too long')
        return name

    @validates('email')
    def validate_email(self, _, email):
        if not email.strip():
            raise UserError('empty email')
        if len(email) < 2 or \
                len(email) > 256 or \
                '@' not in email or \
                '.' not in email or \
                email.startswith('@') or \
                email.endswith('@'):
            raise UserError('invalid email')
        return email


class UserOperator(object):
    def __init__(self, session):
        self.session = session

    def get_user(self, user_id):
        return self.session.query(User).get(user_id)

    def get_user_by_identity(self, provider, identity):
        return self.session.query(User).\
            filter_by(provider=provider).\
            filter_by(identity=identity).first()

    def get_user_by_email(self, email):
        return self.session.query(User).\
            filter(func.lower(User.email) == email.lower()).first()

    def get_user_by_name(self, name):
        return self.session.query(User).\
            filter(func.lower(User.name) == name.lower()).first()

    def create_user(self, user):
        if self.get_user_by_email(user.email):
            raise ModelError('user email exists')
        self.session.add(user)
        self.session.commit()

    def update_user(self, user, **kwargs):
        if 'email' in kwargs:
            found = self.get_user_by_email(kwargs['email'])
            if found and found.id != user.id:
                raise ModelError('user email exists')
        if 'name' in kwargs:
            found = self.get_user_by_name(kwargs['name'])
            if found and found.id != user.id:
                raise ModelError('user name exists')
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.session.commit()

    def delete_user(self, user):
        self.session.delete(user)
        self.session.commit()
