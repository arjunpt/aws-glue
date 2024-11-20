import sys
import os
import pytest  # Import pytest to resolve the undefined name error
from pyspark.sql import SparkSession
from unittest.mock import patch, MagicMock

# Add the 'src' directory to the sys.path so that the test file can import from 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import 'etl' from the 'src' directory
from src.etl import main  # Ensure this points to the right location

@pytest.fixture(scope="session")
def spark_session():
    """Fixture to create a Spark session for testing."""
    return SparkSession.builder \
        .appName("GlueJobTest") \
        .master("local[*]") \
        .getOrCreate()

@patch("awsglue.context.GlueContext", MagicMock())
@patch("awsglue.utils.getResolvedOptions", return_value={
    'JOB_NAME': 'test_job',
    'S3_INPUT_PATH': 's3://mock-input',
    'S3_OUTPUT_PATH': 's3://mock-output',
    'COLUMN_TO_DROP': 'age'
})
def test_etl_logic(spark_session, tmp_path):
    """
    Simple test to validate:
    1. Reading a CSV file.
    2. Dropping a specified column.
    3. Writing output to a local directory.
    """
    # Define test input and output paths using temporary directory
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output"
    column_to_drop = "age"

    # Create sample CSV input data
    input_data = """name,age,city
                    Alice,30,New York
                    Bob,25,Los Angeles
                    Charlie,35,Chicago"""
    input_path.write_text(input_data)

    # Mock AWS Glue job arguments
    args = {
        'JOB_NAME': 'test_job',
        'S3_INPUT_PATH': str(input_path),
        'S3_OUTPUT_PATH': str(output_path),
        'COLUMN_TO_DROP': column_to_drop
    }

    # Patch AWS Glue components
    with patch("awsglue.utils.getResolvedOptions", return_value=args):
        # Import and run your script
        main()  # Execute the ETL script

    # Verify the output
    result_df = spark_session.read.parquet(str(output_path))
    result_data = [row.asDict() for row in result_df.collect()]

    # Expected output after dropping the 'age' column
    expected_data = [
        {"name": "Alice", "city": "New York"},
        {"name": "Bob", "city": "Los Angeles"},
        {"name": "Charlie", "city": "Chicago"}
    ]

    # Check if the output data matches the expected data
    assert result_data == expected_data
