from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    """Data class to represent the artifact of data ingestion process."""
    training_file_path: str
    testing_file_path: str