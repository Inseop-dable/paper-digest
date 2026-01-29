"""Configuration loader for Paper Digest"""

from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """
    Load and validate configuration from YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required fields are missing
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Please copy config.example.yaml to config.yaml and edit it."
        )

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Validate required fields
    _validate_config(config)

    # Apply defaults
    config = _apply_defaults(config)

    return config


def _validate_config(config: dict[str, Any]) -> None:
    """Validate required configuration fields."""

    if not config:
        raise ValueError("Config file is empty")

    # Check interests (required)
    interests = config.get("interests", {})
    if not interests:
        raise ValueError("'interests' section is required in config")

    categories = interests.get("categories", [])
    keywords = interests.get("keywords", [])

    if not categories and not keywords:
        raise ValueError(
            "At least one of 'categories' or 'keywords' must be specified in 'interests'"
        )


def _apply_defaults(config: dict[str, Any]) -> dict[str, Any]:
    """Apply default values for optional fields."""

    # Selection defaults
    selection = config.setdefault("selection", {})
    selection.setdefault("num_papers", 2)
    selection.setdefault("max_candidates", 50)
    selection.setdefault("days_recent", 7)

    # Summary defaults
    summary = config.setdefault("summary", {})
    summary.setdefault("style", "casual")
    summary.setdefault("model", "sonnet")

    # Output defaults
    output = config.setdefault("output", {})
    output.setdefault("directory", "./output/digests")
    output.setdefault("filename_format", "%Y-%m-%d")

    # Notification defaults
    notification = config.setdefault("notification", {})
    notification.setdefault("enabled", True)
    notification.setdefault("sound", "Glass")

    # Advanced defaults
    advanced = config.setdefault("advanced", {})
    advanced.setdefault("api_timeout", 30)
    advanced.setdefault("history_file", "./data/history.json")
    advanced.setdefault("history_retention_days", 90)
    advanced.setdefault("debug", False)

    # Optional sections (can be empty)
    config.setdefault("venues", {})
    config.setdefault("authors", [])

    return config


def get_arxiv_query(config: dict[str, Any]) -> str:
    """
    Build arXiv API query string from configuration.

    Query syntax:
    - Category: cat:cs.LG
    - Title: ti:transformer
    - Abstract: abs:language model
    - Author: au:LeCun
    - Combine with AND/OR

    Args:
        config: Configuration dictionary

    Returns:
        arXiv query string
    """
    interests = config.get("interests", {})
    categories = interests.get("categories", [])
    keywords = interests.get("keywords", [])

    query_parts = []

    # Category query
    if categories:
        cat_query = " OR ".join(f"cat:{cat}" for cat in categories)
        query_parts.append(f"({cat_query})")

    # Keyword query (search in title and abstract)
    if keywords:
        kw_parts = []
        for kw in keywords:
            # Wrap multi-word keywords in quotes
            if " " in kw:
                kw_parts.append(f'ti:"{kw}"')
                kw_parts.append(f'abs:"{kw}"')
            else:
                kw_parts.append(f"ti:{kw}")
                kw_parts.append(f"abs:{kw}")
        query_parts.append(f"({' OR '.join(kw_parts)})")

    # Combine with AND
    if len(query_parts) > 1:
        return " AND ".join(query_parts)
    elif query_parts:
        return query_parts[0]
    else:
        # Fallback
        return "cat:cs.LG"
