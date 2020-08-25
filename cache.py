from datetime import datetime, timedelta


class Cache:
    def __init__(self, expiration_minutes):
        self.expirationMinutes = expiration_minutes
        self.cache = {}
        self.validUntil = datetime.now() + timedelta(minutes=self.expirationMinutes)

    # Add a key and value to the cache
    def add(self, key, value):
        self.cache[key] = value

    # Validate if the key has the same value
    # Also check if the cache still valid
    def validate(self, key, value):
        if self.validUntil < datetime.now():
            self.cache = {}
            self.validUntil = datetime.now() + timedelta(minutes=self.expirationMinutes)

        if key in self.cache:
            if self.cache[key] == value:
                return True

        return False
