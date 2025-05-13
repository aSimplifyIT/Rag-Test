from expiring_dict import ExpiringDict
import os

class CacheHandler:
    def __init__(self):
        self.cache = ExpiringDict()

    def set(self, key, value) -> bool:
        try:
            self.cache.ttl(key, value, int(os.getenv("CONVERSATION_STORING_TIME")))
            return key in self.cache
        
        except Exception:
            return False

    def get(self, key):
        try:
            return self.cache.get(key)
            
        except Exception as e:
            print(f"Error occured in cache get: {e}")

    def delete(self, key) -> bool:
        try:
            if key in self.cache:
                del self.cache[key]
                return True
            else:
                return False
            
        except KeyError:
            return False

    def is_key_exist(self, key) -> bool:
        try:
            if key in self.cache:
                return True
            else:
                return False
            
        except Exception:
            return False
        
    def update_cache_conversation(self, key, values):
        for value in values:
            self.cache[key].append(value)