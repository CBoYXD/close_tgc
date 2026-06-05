from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import (
	AsyncConnection,
	AsyncEngine,
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)

from src.config import settings


class DatabaseSessionManager:
	def __init__(self):
		self._engine: Optional[AsyncEngine] = create_async_engine(
			settings.db_url,
			echo=False,
		)
		self._sessionmaker: Optional[async_sessionmaker[AsyncSession]] = (
			async_sessionmaker(
				autocommit=False,
				expire_on_commit=False,
				bind=self._engine,
			)
		)

	@property
	def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
		if self._sessionmaker is None:
			raise ValueError("Sessionmaker is not initialized")
		return self._sessionmaker

	@property
	def engine(self) -> AsyncEngine:
		if self._engine is None:
			raise ValueError("Engine is not initialized")
		return self._engine

	async def close(self):
		await self.engine.dispose()

		self._sessionmaker = None
		self._engine = None

	@asynccontextmanager
	async def connect(self) -> AsyncIterator[AsyncConnection]:
		async with self.engine.begin() as connection:
			try:
				yield connection
			except Exception:
				await connection.rollback()
				raise

	@asynccontextmanager
	async def session(self) -> AsyncIterator[AsyncSession]:
		session = self.sessionmaker()

		try:
			yield session
		except Exception:
			await session.rollback()
			raise
		finally:
			await session.close()


db_manager = DatabaseSessionManager()


async def get_db():
	async with db_manager.session() as session:
		yield session
