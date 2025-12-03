from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    """Data class to represent the artifact of data ingestion process."""
    training_file_path: str
    testing_file_path: str

@dataclass
class DataValidationArtifact:
    """Data class to represent the artifact of data validation process."""
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str

@dataclass
class DataTransformationArtifact:
    """Data class to represent the artifact of data transformation process."""
    transformed_object_file_path:str
    transformed_train_file_path:str
    transformed_test_file_path:str

@dataclass
class ClassificationMetricArtifact:
    f1_score: float
    precision_score: float
    recall_score: float

@dataclass
class ModelTrainerArtifact:
    """Data class to represent the artifact of model trainer process."""
    trained_model_file_path: str
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact
    