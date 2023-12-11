import importlib.metadata

VERSION = "2023.1031"
PROJECT_NAME = __package__
PROJECT_METADATA = importlib.metadata.metadata(PROJECT_NAME)
PROJECT_URL = PROJECT_METADATA['Project-URL']
