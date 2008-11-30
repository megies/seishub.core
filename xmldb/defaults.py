# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Text, Unicode, DateTime, Boolean 
from sqlalchemy import Numeric
from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.sql import text

from seishub.db.dbmanager import meta as metadata

DEFAULT_PREFIX = 'default_'
DOCUMENT_TABLE = 'document'
DOCUMENT_META_TABLE = 'document_meta'
INDEX_TABLE = 'index'
INDEX_DEF_TABLE = 'index_def'
METADATA_TABLE = 'meta'
METADATA_DEF_TABLE = 'meta_def'
RESOURCE_TABLE = 'resource'

# xmldbms tables:

def revision_default(ctx):
    resource_id = ctx.compiled_parameters[0]['resource_id'] 
    q = text('SELECT coalesce(max(revision), 0) + 1 FROM '+\
             DEFAULT_PREFIX + DOCUMENT_TABLE + ' WHERE resource_id = %s' %\
             resource_id)
    return ctx.connection.scalar(q)

document_tab = Table(DEFAULT_PREFIX + DOCUMENT_TABLE, metadata,
    Column('id', Integer, primary_key = True, autoincrement = True),
    Column('resource_id', Integer),
    Column('revision', Integer, autoincrement = True, 
           default = revision_default),
    Column('data', Unicode),
    UniqueConstraint('resource_id', 'revision'),
    useexisting = True,
    )

document_meta_tab = Table(DEFAULT_PREFIX + DOCUMENT_META_TABLE, metadata,
    Column('id', Integer, primary_key = True), 
    Column('size', Integer),
    Column('datetime', DateTime, default = datetime.now, 
           onupdate = datetime.now),
    Column('uid', Integer),
    Column('hash', String(56)),
    useexisting = True,
    )

# XXX: sqlite does not support autoincrement on combined primary keys
resource_tab = Table(DEFAULT_PREFIX + RESOURCE_TABLE, metadata,
    Column('id', Integer, autoincrement = True, primary_key = True,
           default = text('(SELECT coalesce(max(id), 0) + 1 FROM '+\
                          DEFAULT_PREFIX + RESOURCE_TABLE +')')),
    Column('resourcetype_id', Integer),
    Column('name', String(255), 
           default = text('(SELECT coalesce(max(id), 0) + 1 FROM '+\
                          DEFAULT_PREFIX + RESOURCE_TABLE +')')
           ),
    UniqueConstraint('resourcetype_id', 'name'),
    useexisting=True,
    )

resource_meta_def_tab = Table(DEFAULT_PREFIX + METADATA_DEF_TABLE, metadata,
    Column('id', Integer, primary_key = True, autoincrement = True),
    Column('name', Text),
    Column('type', Text),
    # Column('maxcount', Integer),
    useexisting=True,
    )

resource_meta_tab = Table(DEFAULT_PREFIX + METADATA_TABLE, metadata,
    Column('resource_id', Integer),
    Column('metadata_id', Integer),
    Column('value', Text),
    useexisting=True,
    )

# xmlindexcatalog tables:
#index_def_tab = Table(DEFAULT_PREFIX + INDEX_DEF_TABLE, metadata,
#    Column('id', Integer, primary_key = True, autoincrement = True),
#    Column('value_path', Text),
#    Column('key_path', Text),
#    Column('data_type', String(20)),
#    UniqueConstraint('value_path','key_path'),
#    useexisting=True,
#)
#
#index_tab = Table(DEFAULT_PREFIX + INDEX_TABLE, metadata,
#    Column('id', Integer, primary_key = True, autoincrement = True),
#    Column('index_id', Integer),
#    Column('key', Text),
#    Column('value', Integer),
#    UniqueConstraint('index_id','key','value'),
#    useexisting=True
#)

index_def_tab = Table(DEFAULT_PREFIX + INDEX_DEF_TABLE, metadata,
    Column('id', Integer, primary_key = True, autoincrement = True),
    Column('resourcetype_id', Integer),
    Column('xpath', Text),
    Column('type', Integer),
    Column('options', Text),
    UniqueConstraint('resourcetype_id', 'xpath'),
    useexisting=True,
)

# the following tables correspond to the different possible index types
index_text_tab = Table(DEFAULT_PREFIX + 'text_' + INDEX_TABLE, metadata,
    Column('index_id', Integer),
    Column('key', Unicode),
    Column('document_id', Integer),
    PrimaryKeyConstraint('index_id','key','document_id'),
    useexisting=True
)

index_numeric_tab = Table(DEFAULT_PREFIX + 'numeric_'+ INDEX_TABLE, metadata,
    Column('index_id', Integer),
    Column('key', Numeric),
    Column('document_id', Integer),
    PrimaryKeyConstraint('index_id','key','document_id'),
    useexisting=True
)

index_datetime_tab = Table(DEFAULT_PREFIX + 'datetime_'+ INDEX_TABLE, metadata,
    Column('index_id', Integer),
    Column('key', DateTime),
    Column('document_id', Integer),
    PrimaryKeyConstraint('index_id','key','document_id'),
    useexisting=True
)

index_boolean_tab = Table(DEFAULT_PREFIX + 'boolean_'+ INDEX_TABLE, metadata,
    Column('index_id', Integer),
    Column('key', Boolean),
    Column('document_id', Integer),
    PrimaryKeyConstraint('index_id','key','document_id'),
    useexisting=True
)

index_keyless_tab = Table(DEFAULT_PREFIX + 'keyless_'+ INDEX_TABLE, metadata,
    Column('index_id', Integer),
    Column('document_id', Integer),
    PrimaryKeyConstraint('index_id','document_id'),
    useexisting=True
)