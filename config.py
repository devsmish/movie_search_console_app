import os
from dotenv import load_dotenv


load_dotenv()

# MYSQL_PASSWORD is intentionally excluded: some local MySQL setups run
# with an empty root password, so an empty value there is valid and
# shouldn't be treated as "missing configuration".
REQUIRED_VARS = (
    "MYSQL_HOST",
    "MYSQL_USER",
    "MYSQL_DATABASE",
    "MONGO_URI",
    "MONGO_DATABASE",
    "MONGO_COLLECTION",
)


class ConfigError(Exception):
    """
    Raised when one or more required configuration values are missing.

    Carries the list of missing variable names in `missing`, so callers
    can build a clear, actionable error message instead of letting a
    misconfigured .env surface as a confusing low-level connection error
    deep inside pymysql/pymongo.
    """

    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(", ".join(missing))


class Config:
    # MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

    @classmethod
    def missing_vars(cls) -> list[str]:
        """
        Returns the names of required environment variables that are
        unset or empty (e.g. present in .env.example but never filled in).

        Returns:
            list[str]: Names from REQUIRED_VARS whose value is falsy.
                Empty list if every required variable is set.
        """
        return [name for name in REQUIRED_VARS if not getattr(cls, name)]

    @classmethod
    def validate(cls) -> None:
        """
        Validates that all required configuration values are present.

        Intended to be called once at application startup, before any
        database connection is attempted, so a missing/misnamed .env
        variable produces one clear error instead of a confusing failure
        several layers down inside pymysql or pymongo.

        Raises:
            ConfigError: If one or more required variables are missing.
                `error.missing` lists the missing variable names.
        """
        missing = cls.missing_vars()
        if missing:
            raise ConfigError(missing)
