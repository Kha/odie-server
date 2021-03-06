#! /usr/bin/env python3

import config
import sqlalchemy

from odie import sqla, Column
from sqlalchemy.dialects import postgres
from db import garfield


lecture_docs = sqla.Table('lecture_docs',
        Column('lecture_id', sqla.Integer, sqla.ForeignKey('documents.lectures.id', ondelete='CASCADE')),
        Column('document_id', sqla.Integer, sqla.ForeignKey('documents.documents.id', ondelete='CASCADE')),
        **config.documents_table_args)

folder_lectures = sqla.Table('folder_lectures',
        Column('folder_id', sqla.Integer, sqla.ForeignKey('documents.folders.id', ondelete='CASCADE')),
        Column('lecture_id', sqla.Integer, sqla.ForeignKey('documents.lectures.id', ondelete='CASCADE')),
        **config.documents_table_args)


class Lecture(sqla.Model):
    __tablename__ = 'lectures'
    __table_args__ = config.documents_table_args

    id = Column(sqla.Integer, primary_key=True)
    name = Column(sqla.String)
    aliases = Column(postgres.ARRAY(sqla.String), server_default='{}')
    comment = Column(sqla.String, server_default='')
    validated = Column(sqla.Boolean)

    documents = sqla.relationship('Document', secondary=lecture_docs, lazy='dynamic', back_populates='lectures')
    folders = sqla.relationship('Folder', secondary=folder_lectures, back_populates='lectures')

    def __str__(self):
        return self.name


document_examinants = sqla.Table('document_examinants',
        Column('document_id', sqla.Integer, sqla.ForeignKey('documents.documents.id', ondelete='CASCADE')),
        Column('examinant_id', sqla.Integer, sqla.ForeignKey('documents.examinants.id', ondelete='CASCADE')),
        **config.documents_table_args)

folder_docs = sqla.Table('folder_docs',
        Column('folder_id', sqla.Integer, sqla.ForeignKey('documents.folders.id', ondelete='CASCADE')),
        Column('document_id', sqla.Integer, sqla.ForeignKey('documents.documents.id', ondelete='CASCADE')),
        **config.documents_table_args)


document_type = sqla.Enum('oral', 'written', 'oral reexam', name='document_type', inherit_schema=True)


class Document(sqla.Model):
    __tablename__ = 'documents'
    __table_args__ = config.documents_table_args

    id = Column(sqla.Integer, primary_key=True)
    department = Column(sqla.Enum('mathematics', 'computer science', 'other', name='department', inherit_schema=True))
    date = Column(sqla.Date())
    number_of_pages = Column(sqla.Integer, server_default='0')
    solution = Column(sqla.Enum('official', 'inofficial', 'none', name='solution', inherit_schema=True), nullable=True)
    comment = Column(sqla.String, server_default='')
    document_type = Column(document_type)
    has_file = Column(sqla.Boolean, server_default=sqlalchemy.sql.expression.false())
    validated = Column(sqla.Boolean)
    validation_time = Column(sqla.DateTime(timezone=True), nullable=True)
    submitted_by = Column(sqla.String, nullable=True)
    legacy_id = Column(sqla.Integer, nullable=True)  # old id from fs-deluxe, so we can recognize the old barcodes

    lectures = sqla.relationship('Lecture', secondary=lecture_docs, back_populates='documents')
    examinants = sqla.relationship('Examinant', secondary=document_examinants, back_populates='documents')
    printed_in = sqla.relationship('Folder', secondary=folder_docs, back_populates='printed_docs')

    @property
    def examinants_names(self):
        return [ex.name for ex in self.examinants]

    @property
    def price(self):
        return config.FS_CONFIG['PRICE_PER_PAGE'] * self.number_of_pages


folder_examinants = sqla.Table('folder_examinants',
        Column('folder_id', sqla.Integer, sqla.ForeignKey('documents.folders.id', ondelete='CASCADE')),
        Column('examinant_id', sqla.Integer, sqla.ForeignKey('documents.examinants.id', ondelete='CASCADE')),
        **config.documents_table_args)


class Examinant(sqla.Model):
    __tablename__ = 'examinants'
    __table_args__ = config.documents_table_args

    id = Column(sqla.Integer, primary_key=True)
    name = Column(sqla.String)
    validated = Column(sqla.Boolean)

    documents = sqla.relationship('Document', secondary=document_examinants, lazy='dynamic', back_populates='examinants')
    folders = sqla.relationship('Folder', secondary=folder_examinants, back_populates='examinants')

    def __str__(self):
        return self.name


class Folder(sqla.Model):
    __tablename__ = 'folders'
    __table_args__ = config.documents_table_args

    id = Column(sqla.Integer, primary_key=True)
    name = Column(sqla.String)
    location_id = Column(sqla.Integer, sqla.ForeignKey(garfield.Location.id))
    document_type = Column(document_type)

    location = sqla.relationship(garfield.Location, lazy='joined', uselist=False, back_populates='folders')
    examinants = sqla.relationship('Examinant', secondary=folder_examinants, lazy='subquery', back_populates='folders')
    lectures = sqla.relationship('Lecture', secondary=folder_lectures, lazy='subquery', back_populates='folders')
    printed_docs = sqla.relationship('Document', secondary=folder_docs, back_populates='printed_in')

    def __str__(self):
        return self.name


deposit_lectures = sqla.Table('deposit_lectures',
        Column('deposit_id', sqla.Integer, sqla.ForeignKey('documents.deposits.id', ondelete='CASCADE')),
        Column('lecture_id', sqla.Integer, sqla.ForeignKey('documents.lectures.id', ondelete='CASCADE')),
        **config.documents_table_args)


class Deposit(sqla.Model):
    __tablename__ = 'deposits'
    __table_args__ = config.documents_table_args

    id = Column(sqla.Integer, primary_key=True)
    price = Column(sqla.Integer)
    name = Column(sqla.String)
    by_user = Column(sqla.String)
    date = Column(sqla.DateTime(timezone=True), server_default=sqla.func.now())

    lectures = sqla.relationship('Lecture', secondary=deposit_lectures)
