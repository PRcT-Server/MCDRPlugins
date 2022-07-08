from hashlib import md5
from urllib.request import urlopen
from uuid import UUID

import hjson as json


def get_uuid(name:str):
    try:
        data = json.loads(urlopen(f'https://api.mojang.com/users/profiles/minecraft/{name}').read().decode('utf8'))
        return str(UUID(data['id']))
    except Exception:
        return get_offlineUUID(name)

def get_offlineUUID(name:str):

    data = f"OfflinePlayer:{name}"

    hash = md5(data.encode("utf-8")).digest()

    byte_array = [byte for byte in hash]

    byte_array[6] = hash[6] & 0x0f | 0x30
    byte_array[8] = hash[8] & 0x3f | 0x80

    return str(UUID(bytes(byte_array).hex()))
