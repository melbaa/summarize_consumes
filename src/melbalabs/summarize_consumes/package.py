import importlib.metadata

VERSION = "2025.1114"
PROJECT_NAME = __package__
PROJECT_METADATA = importlib.metadata.metadata(PROJECT_NAME)
PROJECT_URL = PROJECT_METADATA["Project-URL"]
