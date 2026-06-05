"""
This module contains the Pydantic schemas for the Payment model.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.database.enums.payment import PaymentStatus


class PaymentCreate(BaseModel):
	"""
	Schema for creating a Payment.
	"""

	id: int
	user_id: int
	currency: str = "USDT"
	amount: float
	status: PaymentStatus = PaymentStatus.PENDING
	pay_url: str


class PaymentUpdate(BaseModel):
	"""
	Schema for updating a Payment.
	"""

	status: Optional[PaymentStatus] = None
	fee: Optional[float] = None
	paid_at: Optional[datetime] = None
