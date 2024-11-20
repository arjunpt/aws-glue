import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job

# Arguments: Input and output paths, and the column to drop
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_INPUT_PATH', 'S3_OUTPUT_PATH', 'COLUMN_TO_DROP'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read CSV data from S3 using PySpark DataFrame
input_path = args['S3_INPUT_PATH']
output_path = args['S3_OUTPUT_PATH']
column_to_drop = args['COLUMN_TO_DROP']

# Load the CSV data into a PySpark DataFrame
data_frame = spark.read.option("header", "true").csv(input_path)

# Drop the specified column
data_frame = data_frame.drop(column_to_drop)

# Write the DataFrame to S3 in Parquet format
data_frame.write.mode("overwrite").parquet(output_path)

job.commit()
