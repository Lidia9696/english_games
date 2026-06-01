# Utility functions shared across all games

import random
import string


def generate_room_code():
    """Generate random 4-character room code (letters + digits)"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=4))