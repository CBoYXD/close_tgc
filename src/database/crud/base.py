"""
This module contains the base CRUD class for basic operations.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.base import AbstractBaseModel

# pylint: disable=invalid-name
ModelType = TypeVar("ModelType", bound=AbstractBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel)
# pylint: enable=invalid-name


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
	"""
	Generic CRUD class for basic operations.
	"""

	def __init__(self, model: type[ModelType]):
		self.model = model

	def get_dict_from_orm_object(self, orm_object: ModelType) -> dict:
		"""
		Converts an ORM object to a dictionary where the keys are the column names
		and the values are the corresponding attribute values of the ORM object.
		Args:
		    orm_object (ModelType): An instance of the ORM model from which data is extracted.
		Returns:
		    dict: A dictionary representation of the ORM object with column names as keys.
		"""
		return {
			column.name: getattr(orm_object, column.name)
			for column in self.model.__table__.columns
		}

	async def create(
		self, db: AsyncSession, obj_in: CreateSchemaType
	) -> ModelType:
		"""
		Create a new object.
		:param db: Database session.
		:param obj_in: Object to create.
		:return: Object created.
		"""
		db_obj = self.model(**obj_in.model_dump(exclude_none=True))
		db.add(db_obj)
		await db.commit()
		await db.refresh(db_obj)
		return db_obj

	async def get_by_id(
		self, db: AsyncSession, obj_id: int
	) -> Optional[ModelType]:
		"""
		Get an object by ID.
		"""

		query = select(self.model).where(self.model.id == obj_id)
		result = await db.execute(query)
		return result.scalar_one_or_none()

	async def get_all(self, db: AsyncSession) -> list[ModelType]:
		"""
		Get all objects of the model.
		"""
		query = select(self.model)
		result = await db.execute(query)
		return list(result.scalars().all())

	async def update(
		self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType
	) -> ModelType:
		"""
		Update an object.
		:param db: Database session.
		:param db_obj: Database object to update.
		:param obj_in: Data to update.
		:return: Updated object.
		"""
		obj_data = obj_in.model_dump(exclude_none=True)
		for field, value in obj_data.items():
			setattr(db_obj, field, value)
		db.add(db_obj)
		await db.commit()
		await db.refresh(db_obj)
		return db_obj

	async def delete(self, db: AsyncSession, db_obj: ModelType) -> None:
		"""
		Delete an object.
		:param db: Database session.
		:param db_obj: Database object to delete.
		:return: None
		"""
		await db.delete(db_obj)
		await db.commit()
