
import sys

from umbrellamouth import * 

# TODO EXTENSIVE TESTING!!!!

@with_cursor
def len_(queue, cursor=None):
    # TODO might need quotes around attribute
    cursor.execute('''
        SELECT COUNT(*) FROM umbrellamouth WHERE attribute = ?
    ''', (queue,))
    result = cursor.fetchone()
    return result[0] if result else 0 

@with_cursor
def index_(queue, entry, cursor=None):
    cursor.execute('''
        SELECT value 
        FROM umbrellamouth 
        WHERE entry = ? AND attribute = ? 
    ''', (entry, queue,))
    result = cursor.fetchone()
    
    if not result: return None
    if result[0] is None: return None
    return int(result[0])

@with_cursor
def insert_(queue, entry, index, cursor=None):
    index = min(index, len_(queue, cursor=cursor)-1)
    if index == -1:
        index = len_(queue, cursor=cursor) - 1
    index = max(0, index)

    current_index = index_(queue, entry, cursor=cursor)

    if current_index is None:
        cursor.execute('''
            UPDATE umbrellamouth 
            SET value = CAST(value AS INTEGER) + 1
            WHERE attribute = ? AND CAST(value AS INTEGER) >= ?
        ''', (queue, index))
    else:
        if index > current_index:
            cursor.execute('''
                UPDATE umbrellamouth
                SET value = CAST(value AS INTEGER) - 1
                WHERE attribute = ? 
                AND CAST(value AS INTEGER) > ? 
                AND CAST(value AS INTEGER) <= ?
            ''', (queue, current_index, index))
        elif index < current_index:
            cursor.execute('''
                UPDATE umbrellamouth 
                SET value = CAST(value AS INTEGER) + 1
                WHERE attribute = ? 
                AND CAST(value AS INTEGER) >= ? 
                AND CAST(value AS INTEGER) < ?
            ''', (queue, index, current_index))

    save_attr(entry, queue, index, cursor=cursor)
        
@with_cursor
def remove_(queue, entry, cursor=None):
    current_index = index_(queue, entry, cursor=cursor)
    
    if current_index is not None:
        cursor.execute('''
            DELETE FROM umbrellamouth 
            WHERE entry = ? 
            AND attribute = ? 
        ''', (entry, queue,))
        
        cursor.execute('''
            UPDATE umbrellamouth 
            SET value = CAST(value AS INTEGER) - 1
            WHERE attribute = ?
            AND CAST(value AS INTEGER) > ?
        ''', (queue, current_index,))

@with_cursor
def empty_(queue, cursor=None):
    cursor.execute('''
        DELETE FROM umbrellamouth WHERE attribute = ? 
    ''', (queue,))

@with_cursor
def pos_to_perc(queue, pos, cursor=None):
    total = len_(queue=queue, cursor=cursor) 
    if total == 0: return 0
    return pos / total

@with_cursor
def perc_to_pos(queue, perc, cursor=None):
    total = len_(queue=queue, cursor=cursor) 
    if total == 0: return 0
    return round(perc * total)
