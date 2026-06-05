from datetime import timedelta
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=".env",
		extra="ignore",
		env_file_encoding="utf-8",
	)

	bot_token: str
	closed_channel_id: int
	payment_link: str
	payment_token: str
	pay_amount: int = 10

	# Redis
	redis_host: str = "localhost"
	redis_port: int = 6379
	redis_db: int = 0

	# Postgres
	db_driver: str = "postgresql+asyncpg"
	db_name: str = Field(default="db_name", alias="POSTGRES_DB")
	db_user: str = Field(default="user", alias="POSTGRES_USER")
	db_password: str = Field(default="password", alias="POSTGRES_PASSWORD")
	db_host: str = "db"
	db_port: int = 5432

	@computed_field
	@property
	def redis_url(self) -> str:
		"""
		Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
		"""
		return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

	@computed_field
	@property
	def db_url(self) -> URL:
		"""
		Computed property to get SQLAlchemy URL, using env settings
		"""
		return URL.create(
			drivername=self.db_driver,
			username=self.db_user,
			password=self.db_password,
			host=self.db_host,
			database=self.db_name,
			port=self.db_port,
		)

	@property
	def reminders(self) -> list[timedelta]:
		"""
		Scheduled reminder messages to send after initial contact.
		"""
		return [
			timedelta(minutes=30),
			timedelta(days=1),
			timedelta(days=2),
			timedelta(days=3),
		]

	@property
	def reminders_count(self) -> int:
		"""
		Number of scheduled reminder messages configured.
		"""
		return len(self.reminders)

	@property
	def template_path(self) -> str:
		"""
		Path to the templates directory.
		"""
		return Path(__file__).parent / "templates"


settings = Settings()
