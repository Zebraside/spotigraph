class DB:
    POSTGRES_NAME = "postgres"
    POSTGRES_PASS = "nkp47FRy"
    POSTGRES_SERVER = "localhost"
    POSTGRES_PORT = "5432"
    POSTGRES_DB = "postgres"


class MQ:
    SCRAPPER_QUEUE_NAME = "scrapper"
    ARTISTS_QUEUE_NAME = "artists"


class InjectionConfig:
    INJECTION_COUNT = 10
    INJECTION_DELAY_SEC = 10