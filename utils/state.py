"""
Хранит состояние между модулями без циклических импортов.
admin_chat_id обновляется при каждом сообщении от администратора.
"""
import os

_FILE = ".admin_chat_id"
admin_chat_id: int = 0


def save(chat_id: int):
    global admin_chat_id
    admin_chat_id = chat_id
    try:
        with open(_FILE, "w") as f:
            f.write(str(chat_id))
    except Exception:
        pass


def load() -> int:
    global admin_chat_id
    if admin_chat_id:
        return admin_chat_id
    try:
        with open(_FILE) as f:
            admin_chat_id = int(f.read().strip())
    except Exception:
        pass
    return admin_chat_id
