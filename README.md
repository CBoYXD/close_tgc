# Rust Digest Bot

Rust Digest Bot is a Telegram bot for selling access to a private Rust programming channel.

The project includes:

- a public promo dialog for the Rust channel;
- FAQ and onboarding screens;
- payment invoice creation and payment status checks;
- one-time invite links for a closed Telegram channel;
- UTM tracking for promo links;
- admin statistics;
- scheduled payment-return messages for users who did not finish payment.

The bundled copy presents a private Rust channel with technical summaries, book notes, curated reading paths, crate reviews, and production-oriented Rust explanations.

## Tech Stack

- Python 3.12
- aiogram 3
- aiogram-dialog
- SQLAlchemy and Alembic
- PostgreSQL
- Redis
- APScheduler

## Configuration

Create a `.env` file with the required settings:

```env
BOT_TOKEN=
CLOSED_CHANNEL_ID=
PAYMENT_LINK=
PAYMENT_TOKEN=
PAY_AMOUNT=10
POSTGRES_DB=rust_digest
POSTGRES_USER=rust_digest
POSTGRES_PASSWORD=change-me
```

## Development

Install dependencies:

```bash
uv sync
```

Run the app with Docker Compose:

```bash
docker compose up --build
```

Run migrations:

```bash
alembic upgrade head
```

## Content

Promo texts live in `src/templates`.
Return-message texts live in `src/templates/reminders`.
