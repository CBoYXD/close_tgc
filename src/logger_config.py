"""
Logging configuration for the application.
"""

import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from os import getcwd
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

# Logging configuration constants
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup files

# Define Kyiv timezone (handles DST automatically)
KYIV_TZ = ZoneInfo("Europe/Kyiv")


class UTC3Formatter(logging.Formatter):
	"""Custom formatter that forces all timestamps to UTC+3."""

	def formatTime(self, record, datefmt=None):
		dt = datetime.fromtimestamp(record.created, KYIV_TZ)
		if datefmt:
			return dt.strftime(datefmt)
		return dt.isoformat()


def setup_logger(
	name: str,
	use_file: bool = True,
	max_bytes: Optional[int] = None,
	backup_count: Optional[int] = None,
) -> logging.Logger:
	"""Setup a logger with UTC+3 time formatting.

	If use_file is True, attaches a RotatingFileHandler. Otherwise, attaches
	a StreamHandler for console output. Prevents duplicate handlers on reuse.
	"""

	# Create logger
	logger = logging.getLogger(name)
	logger.setLevel(logging.INFO)

	# Prevent duplicate handlers if logger is reused
	if logger.handlers:
		return logger

	# Prepare handler depending on target
	if use_file:
		# Create logs directory if it doesn't exist
		log_dir = Path(getcwd()) / "logs"
		log_dir.mkdir(exist_ok=True)

		# Use provided values or defaults
		max_bytes = max_bytes or MAX_LOG_FILE_SIZE
		backup_count = backup_count or BACKUP_COUNT

		# Create rotating file handler with size restrictions
		log_file_name = f"{name}.log"
		handler = RotatingFileHandler(
			log_dir / log_file_name,
			maxBytes=max_bytes,
			backupCount=backup_count,
			encoding="utf-8",
		)
	else:
		# Log to console (stderr by default)
		handler = logging.StreamHandler()
	handler.setLevel(logging.INFO)

	# Create formatter with UTC+3
	formatter = UTC3Formatter(
		"%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S %z",
	)
	handler.setFormatter(formatter)

	# Add handler to logger
	logger.addHandler(handler)
	# Avoid double logging to root
	logger.propagate = False

	return logger


def get_logger(
	name: str,
	use_file: bool = True,
	max_bytes: Optional[int] = None,
	backup_count: Optional[int] = None,
) -> logging.Logger:
	"""Get a logger for a specific service with file size restrictions."""
	return setup_logger(
		name=name,
		use_file=use_file,
		max_bytes=max_bytes,
		backup_count=backup_count,
	)
