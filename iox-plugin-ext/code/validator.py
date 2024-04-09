
#!/usr/bin/env python3

"""
Useful validation routines
Copyright (C) 2024 Universal Devices
"""
from log import LOGGER
import re

def validate_id(id)->bool:
    if id == None:
        LOGGER.critical('validate_id - missing object ...')
        return False
    try:
        if id == None or id == '':
            LOGGER.critical('validate_id - id does not exist ... ') 
            return False

        #cannot have spaces in ids
        return not re.search(" ", id)

    except Exception as ex:
        raise
