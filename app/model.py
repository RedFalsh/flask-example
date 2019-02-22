#!/usr/bin/env python
# encoding: utf-8

from app import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    password = db.Column(db.String(32))
    telephone = db.Column(db.String(15))

    def __init__(self, name, password, telephone):
        self.name = name
        self.password = password
        self.telephone = telephone

    def __repr__(self):
        return '<id {}>'.format(self.id)

