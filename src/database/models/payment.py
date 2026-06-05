"""
Admin model for storing admin credentials
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.enums.payment import PaymentStatus

from .base import AbstractBaseModel

if TYPE_CHECKING:
	from .user import User


class Payment(AbstractBaseModel):
	"""
	Payment model for storing payment information
	"""

	user_id: Mapped[int] = mapped_column(
		ForeignKey("users.id"), comment="Reference to User"
	)
	user: Mapped["User"] = relationship()
	currency: Mapped[str] = mapped_column(
		String(10),
		default="USDT",
		comment="Currency of the payment",
	)
	amount: Mapped[float] = mapped_column(
		comment="Amount paid",
	)
	status: Mapped[PaymentStatus] = mapped_column(
		SQLAlchemyEnum(
			PaymentStatus, values_callable=lambda obj: [e.value for e in obj]
		),
		default=PaymentStatus.PENDING,
		comment="Status of the payment",
	)
	pay_url: Mapped[str] = mapped_column(
		String(100),
		comment="Payment URL",
	)
	paid_at: Mapped[Optional[datetime]] = mapped_column(
		DateTime(timezone=True),
		comment="Timestamp when payment was completed",
	)
	fee: Mapped[Optional[float]] = mapped_column(
		comment="Transaction fee",
	)
