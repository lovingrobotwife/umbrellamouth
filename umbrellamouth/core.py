
import os
import re
import sys
import uuid
import json
import sqlite3
import functools
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import contextmanager

START_OF_DAY = '0400'
DEFAULT_PRIORITY_PERC = 0.5
DEFAULT_SCHEDULER = 'invariable 1'

COLL = '/home/orange/000'
DB = '/home/orange/000/.umbrellamouth/umbrellamouth.db'

## eh
COLL = Path(COLL)
DB = Path(DB)
DB.parent.mkdir(parents=True, exist_ok=True)
if not DB.is_file(): DB.touch()

# ---

def parse_stdin():
    return [x.strip() for x in sys.stdin.readlines()] if not sys.stdin.isatty() else None

def is_uuid(x):
    try: uuid.UUID(x); return True
    except ValueError: return False

def uuid_regex(x):
    pattern = r'(?:[0-9a-f]{32}|[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})'
    return [match.group().strip() for match in re.finditer(pattern, x, re.IGNORECASE)]

def recursive_scandir(directory):
    for entry in os.scandir(directory):
        if entry.is_dir(follow_symlinks=False):
            yield from recursive_scandir(entry.path)
            continue

        yield Path(entry)

def with_cursor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'cursor' not in kwargs:
            with db_cursor() as (c, _):
                return func(*args, cursor=c, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper

@with_cursor
def init_db(cursor=None):
    cursor.execute('''
        create table if not exists umbrellamouth (
            entry text not null,
            attribute text not null,
            value text, 
            unique (entry, attribute)
        )
    ''')

@contextmanager
def db_cursor():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        yield cursor, conn 
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

@with_cursor
def save_attr(entry, attr, value, cursor=None):
    value = json.dumps(value)

    cursor.execute('''
        INSERT INTO umbrellamouth (entry, attribute, value)
        VALUES (?, ?, ?)
        ON CONFLICT(entry, attribute) DO UPDATE SET value=excluded.value
    ''', (entry, attr, value))

@with_cursor
def save_attrs(entry, attrs, cursor=None):
    # TODO delete attrs that have been removed from dict
    for attr, value in attrs.items():
        save_attr(entry, attr, value, cursor=cursor)

@with_cursor
def attrs_(entry, cursor=None):
    cursor.execute('''
        SELECT * FROM umbrellamouth 
        WHERE entry = ?
    ''', (entry,))

    attrs = {}
    for entry, attr, value in cursor.fetchall():
        attrs[attr] = json.loads(value)

    return attrs

def scan_coll_for_entry(entry):
    for path in recursive_scandir(COLL):
        if path.stem == entry:
            return path
    return None

def find_entry_path(entry, attrs):
    path = attrs.get('path')

    if path is None:
        return scan_coll_for_entry(entry)

    # this is converting relative path to absolute
    path = Path(path)
    path = (COLL / path).absolute() # TODO double check

    if path.is_file():
        return path

    return scan_coll_for_entry(entry)

def find_uuids(xs):
    if xs is None: return None
    if not isinstance(xs, list): xs = [xs]

    for x in xs:
        if not isinstance(x, str):
            try:
                x = str(x)
            except TypeError:
                return None

        if is_uuid(x):
            yield x; continue

        for x in uuid_regex(x):
            yield x; continue

@with_cursor
def parse(xs, cursor=None):
    for entry in find_uuids(xs):
        attrs = attrs_(entry, cursor=cursor) 

        # make sure exists
        path = find_entry_path(entry, attrs)
        if path is None:
            continue
        
        yield entry, attrs

def is_hidden(path):
    for part in path.parts:
        if part.startswith('_') or part.startswith('.'):
            return True
    return False

def is_in_coll(path):
    if str(path.parent).startswith(str(COLL)): return True
    return False

def entry_(): 
    return uuid.uuid4().hex

@with_cursor
def init_priority(entry, attrs, cursor=None):
    # TODO is this the best way to handle it?

    if attrs.get('priority') is not None:
        return None

    from .queue import perc_to_pos, insert_

    index = perc_to_pos('priority', 
                        DEFAULT_PRIORITY_PERC,
                        cursor=cursor) 
    insert_('priority', entry, index, cursor=cursor)

def default_attrs():
    return {
        'ctime': int(datetime.now().timestamp()),
        'due': int((datetime.now() + timedelta(days=1)).timestamp()),
        'interval': 1,
    }

def relative_to_coll(path):
    if not is_in_coll(path): 
        raise Exception('path not in coll')

    return f'./{path.relative_to(COLL)}'


init_db() # TODO this is lazy
