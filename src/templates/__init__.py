"""
Template utilities for rendering Jinja2 templates
"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.config import settings

# Get the directory where this file is located
TEMPLATES_DIR = settings.template_path

# Create Jinja2 environment
env = Environment(
	loader=FileSystemLoader(
		[str(TEMPLATES_DIR), str(TEMPLATES_DIR / "reminders")]
	),
	trim_blocks=True,
	lstrip_blocks=True,
	autoescape=False,  # Disable auto-escaping to allow HTML tags in templates
)


def render_template(template_name: str, **kwargs: Any) -> str:
	"""
	Render a Jinja2 template with the given context.

	Args:
	    template_name: Name of the template file (without .jinja extension)
	    **kwargs: Template variables

	Returns:
	    Rendered template as string
	"""
	template = env.get_template(f"{template_name}.jinja")
	return template.render(**kwargs)
