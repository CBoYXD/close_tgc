from enum import StrEnum


class PaymentStatus(StrEnum):
	PENDING = "pending"
	COMPLETED = "completed"
	FAILED = "failed"
