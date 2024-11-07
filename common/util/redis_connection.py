import redis

from common.logging.logger import LOGGER
from common.util.environment import env


class RedisConnectionPool:
    # sentinel: redis.sentinel.Sentinel
    redis: redis.client.Redis
    MAX_LIST_LENGTH: int = 6

    async def startup(self):
        # self.sentinel, self.redis = redis_sentinel_url.connect(env.get("REDIS_URL"))
        LOGGER.info("Connecting to Redis")
        self.redis = redis.Redis(host=env.get("REDIS_HOST"), port=env.get("REDIS_PORT"))

    async def shutdown(self):
        LOGGER.info("Disconnecting to Redis")
        self.redis.close()

    async def put(self, key: str, value: str, ex: int = int(env.get("REDIS_DEFAULT_TTL"))):
        # 신규 데이터 저장
        self.redis.set(name=key, value=value, ex=ex)

    async def set_ttl(self, key: str, value: str, ex: int = int(env.get("REDIS_DEFAULT_TTL"))):
        # 신규 데이터 저장
        self.redis.setex(name=key, time=ex, value=value)

    async def remove(self, key: str):
        # 데이터 삭제
        self.redis.delete(key)

    async def get(self, key: str):
        # 데이터 조회
        return self.redis.get(key)

    async def scan_iter(self, pattern: str):
        keys = []
        for key in self.redis.scan_iter(pattern):
            keys.append(key)
        return keys

    def lpush(self, key: str, *values):
        # 하나의 key에 대해 여러 개의 value를 넣을 때 사용한다
        # 새로운 데이터는 head에 추가된다 (index 0으로 추가됨)
        self.redis.lpush(key, *values)
        # self.redis.ltrim(key, 0, 5)
        # lpush 파라미터 중 expire date 설정이 따로 존재하지 않아 expire 코드를 별도로 추가함
        self.redis.expire(key, int(env.get("REDIS_DEFAULT_TTL")))

    def lrange(self, key: str, start: int, end: int):
        # 하나의 key에 대해 여러 개의 value가 저장될 경우, 해당 value를 가져올 때 사용한다.
        # start와 end 값에는 불러오고자하는 데이터의 index 값을 넣는다.
        return self.redis.lrange(key, start, end)

    def get_connection(self):
        # redis와의 connection 정보 반환
        return self.redis

    @staticmethod
    def get_url():
        return f"redis://{env.get('REDIS_HOST')}:{env.get('REDIS_PORT')}"

    def get_redis_keys_and_sizes(self, pattern="*"):
        # Redis 연결 설정
        client = redis.Redis(host='localhost', port=6379, db=0)

        # 패턴에 따라 키 목록 조회
        keys = client.keys(pattern)
        key_sizes = {}

        # 각 키의 사이즈 확인
        for key in keys:
            key_type = client.type(key).decode("utf-8")

            if key_type == "string":
                size = client.strlen(key)  # 문자열 길이
            elif key_type == "list":
                size = client.llen(key)  # 리스트 길이
            elif key_type == "set":
                size = client.scard(key)  # 집합의 원소 개수
            elif key_type == "zset":
                size = client.zcard(key)  # 정렬 집합의 원소 개수
            elif key_type == "hash":
                size = client.hlen(key)  # 해시의 필드 개수
            else:
                size = "Unknown type"

            key_sizes[key.decode("utf-8")] = size

        return key_sizes


redis_connection_pool = RedisConnectionPool()
