"""
This module contains the CRUD operations for the Payment model.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.crud.base import CRUDBase
from src.database.models.payment import Payment
from src.database.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentCRUD(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
	"""
	CRUD class for the Payment model.
	"""

	async def get_by_user_id(
		self, db: AsyncSession, user_id: int
	) -> Optional[Payment]:
		"""
		Retrieve payments by user_id.
		"""
		statement = select(self.model).where(self.model.user_id == user_id)
		result = await db.execute(statement)
		return result.scalar_one_or_none()


payment_crud = PaymentCRUD(Payment)
