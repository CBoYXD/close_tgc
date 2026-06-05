"""Payment service helpers for creating invoices and checking status.

This module implements a small async client for a generic Crypto-pay provider.
It expects two settings in `src.config.settings`: `payment_link` (the base
API URL for the provider) and `payment_token` (secret or API token). The
provider-specific endpoints are not hard-coded beyond using the base URL,
so configure `payment_link` accordingly (for example,
`https://api.send.tg/v1/invoices`).

Functions:
- create_invoice: POST to the provider to create an invoice and return
  a dict with at least `invoice_id` and `payment_url` if available.
- generate_link: wrapper that creates an invoice and returns the payment URL
  (and invoice id) to the caller.
- check_payment: query the invoice status by invoice id and return True when
  completed.
"""

from typing import Any

import aiohttp

from src.config import settings
from src.database.crud.payment import payment_crud
from src.database.enums.payment import PaymentStatus
from src.database.schemas.payment import PaymentCreate, PaymentUpdate
from src.database.setup import db_manager


class PaymentService:
	"""Payment service client for creating invoices and checking status."""

	urls = {
		"create_invoice": "createInvoice",
		"get_invoice": "getInvoices",
	}
	headers = {
		"Crypto-Pay-API-Token": settings.payment_token,
		"Content-Type": "application/json",
	}

	def url(self, name: str) -> str:
		"""Construct full URL for a given endpoint name."""
		return f"{settings.payment_link}/api/{self.urls[name]}"

	async def create_invoice(
		self,
		user_id: int,
		currency: str = "USDT",
	) -> dict[str, Any]:
		"""Create an invoice at the configured payment provider.

		The function will POST a JSON payload to `settings.payment_link`. How the
		provider expects the body may vary; we use a sensible generic format.

		Returns the parsed JSON response. Caller should handle missing fields.
		"""

		payload: dict[str, Any] = {
			"description": "Оплата за закрытый доступ к каналу",
			"amount": settings.pay_amount,
			"currency_type": "crypto",
			"asset": currency,
		}

		async with aiohttp.ClientSession() as session:
			async with session.post(
				self.url("create_invoice"),
				json=payload,
				headers=self.headers,
				timeout=20,
			) as resp:
				# Try best-effort parsing; raise for network/HTTP errors
				resp.raise_for_status()
				data = await resp.json()
				result = data["result"]

		async with db_manager.session() as db:
			await payment_crud.create(
				db,
				PaymentCreate(
					id=result["invoice_id"],
					user_id=user_id,
					amount=settings.pay_amount,
					currency=currency,
					pay_url=result["bot_invoice_url"],
				),
			)

		return result["bot_invoice_url"]

	async def check_payment(self, invoice_id: int) -> bool:
		"""Check invoice status using invoice_id.

		If `invoice_id` is None this function returns False. This function assumes
		the provider exposes an endpoint at `<payment_link>/<invoice_id>` that
		returns JSON containing a `status` field equal to `completed` when paid.
		Adjust to match your provider.
		"""

		data = {"invoice_ids": invoice_id}

		async with aiohttp.ClientSession() as session:
			async with session.get(
				self.url("get_invoice"),
				headers=self.headers,
				timeout=20,
				params=data,
			) as resp:
				resp.raise_for_status()
				data = await resp.json()
				result = data["result"]["items"][0]

		if result["status"] == "paid":
			async with db_manager.session() as db:
				payment = await payment_crud.get_by_id(db, invoice_id)
				await payment_crud.update(
					db,
					db_obj=payment,
					obj_in=PaymentUpdate(
						status=PaymentStatus.COMPLETED,
						paid_at=result["paid_at"],
						fee=result["fee_amount"],
					),
				)
			return True
		return False


payment_service = PaymentService()
