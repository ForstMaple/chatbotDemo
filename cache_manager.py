import logging
import redis
import toml

logger = logging.getLogger("bot." + __name__)
config = toml.load('config.toml')

r = redis.Redis(host=config["redis"]["host"], port=config["redis"]["port"], db=0)
logging.info("Redis connection established.")


def set_user_state(user_id, key, value):
    r.hset(f"{user_id}_state", key, value)


def get_user_state(user_id, key):
    return r.hget(f"{user_id}_state", key)


def del_user_state(user_id, key):
    r.hdel(f"{user_id}_state", key)
