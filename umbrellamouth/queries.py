
from umbrellamouth import *

@with_cursor
def outstanding(cursor=None):
    timestamp = get_next_start_of_day().timestamp() 
    
    cursor.execute('''
        SELECT entry
        FROM umbrellamouth 
        WHERE attribute = 'due'
        AND CAST(value AS INTEGER) <= ?
    ''', (timestamp,)) # TODO sort by priority here

    return [entry[0] for entry in cursor.fetchall()]

@with_cursor
def outstanding_priority_sort(cursor=None): # TODO TEST
    timestamp = get_next_start_of_day().timestamp() 

    cursor.execute('''
        SELECT due.entry
        FROM umbrellamouth AS due
        JOIN umbrellamouth AS prio
          ON due.entry = prio.entry
        WHERE due.attribute = 'due'
          AND CAST(due.value AS INTEGER) <= ?
          AND prio.attribute = 'priority'
        ORDER BY CAST(prio.value AS INTEGER) ASC
    ''', (timestamp,))

    return [entry[0] for entry in cursor.fetchall()]
