import redis
from django.core.cache import cache
import os

# config
redis_host = "localhost"
redis_port = 6379
#redis_url = os.environ['REDIS_URL']
redis_password = ""
redis_key_prefix = "euros-data/"
redis_matches_prefix = "leaderboard-after-"


# def connect_to_redis():
#     try:
#
#         # The decode_repsonses flag here directs the client to convert the responses from Redis into Python strings
#         # using the default encoding utf-8.  This is client specific.
#         r = redis.from_url(redis_url)
#         return r
#
#     except Exception as e:
#         print(e)
#         return None


def get_redis_matches_key(count):
    return redis_key_prefix+redis_matches_prefix+str(count)+"/"


def get_leaderboard_from_redis(key):

    try:
        # The decode_repsonses flag here directs the client to convert the responses from Redis into Python strings
        # using the default encoding utf-8.  This is client specific.
        pointsdata = {}
        for i in range(1,100):
            points = cache.get(key+str(i))
            if points is not None and points != "":
                print("get",points)
                pointsdata[str(i)] = points
        if len(pointsdata.values()) == 0:
            return None
        else:
            return pointsdata
    except Exception as e:
        print(e)
        return None


def write_leaderboard_to_redis(key, leaderboard):
    print(key, str(leaderboard))
    try:
        # The decode_repsonses flag here directs the client to convert the responses from Redis into Python strings
        # using the default encoding utf-8.  This is client specific.
        for pkey,value in leaderboard.items():
            cache.set(key+str(pkey), str(value))

    except Exception as e:
        print(e)
