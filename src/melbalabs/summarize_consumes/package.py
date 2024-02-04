import importlib.metadata

VERSION = "2024.1052"
PROJECT_NAME = __package__
PROJECT_METADATA = importlib.metadata.metadata(PROJECT_NAME)
PROJECT_URL = PROJECT_METADATA['Project-URL']
