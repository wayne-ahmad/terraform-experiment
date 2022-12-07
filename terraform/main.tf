provider "aws" {
  region = "eu-west-2"

  default_tags {
    tags = {
      project = "TDSA"
    }
  }
}

# =====================================================
#                    configure

# lambda configure 

variable "lambda_config" {
  type = map(any)
  default = {
    function_name = "tdsa_query_processor_test"
    handler       = "lambda_function.lambda_handler"
  }
}

# =====================================================

# add in a lambda layer

resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "../lambda_layer/pyodbc-f42da674-0585-490d-8d46-d58307ea2001.zip"
  layer_name = "pyodbc_lambda_layer_name"

  compatible_runtimes = ["python3.7", "python3.8"]
}

# create queue policy

# create a sqs 
resource "aws_sqs_queue" "Data_order_queue" {
  name                       = "Data_order_queue"
  visibility_timeout_seconds = 120
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 345600
  receive_wait_time_seconds  = 0
  sqs_managed_sse_enabled    = false

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.delivery_failure_queue.arn
    maxReceiveCount     = 10
  })

  tags = {
    Environment = "testing"
  }
}

# create dead letter queue
# Delivery failure queue
resource "aws_sqs_queue" "delivery_failure_queue" {
  name                      = "delivery_failure_queue"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  receive_wait_time_seconds = 10
  sqs_managed_sse_enabled   = false

  tags = {
    Environment = "testing"
  }
}

# subscribe Lambda function to SQS 
resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  event_source_arn                   = aws_sqs_queue.Data_order_queue.arn
  enabled                            = true
  function_name                      = aws_lambda_function.lambda.arn
  batch_size                         = 5
  maximum_batching_window_in_seconds = 30
}


# creating a bucket for the deployment zip into the lambda function
resource "aws_s3_bucket" "deployment-bucket" {
  bucket = "deployment-zip-bucket-tdsa"
  tags = {
    Name        = "Deployment bucket"
    Environment = "Test"
  }
}


# lambda function, loading zip from deployment-bucket, role python
resource "aws_lambda_function" "lambda" {

  function_name = var.lambda_config.function_name
  # filename         = data.archive_file.lambda.output_path
  source_code_hash = sha256(file(data.local_file.deploy-zip.filename))
  s3_bucket        = aws_s3_bucket.deployment-bucket.bucket
  s3_key           = aws_s3_object.file_upload.key
  role             = aws_iam_role.lambda_role.arn
  handler          = var.lambda_config.handler
  runtime          = "python3.7"
  layers           = [aws_lambda_layer_version.lambda_layer.arn]
  timeout          = 120

  # adding environment variables
  environment {
    variables = {
      ORDER_QUEUE             = "DataOrder"
      PROCESSED_ORDERS_BUCKET = "processedenquiries"

    }
  }
}

data "local_file" "deploy-zip" {
  filename = "../deploy.zip"
}


# uploading deployment zip to deployment bucket
resource "aws_s3_object" "file_upload" {
  bucket = aws_s3_bucket.deployment-bucket.id
  key    = "lambda-deployment.zip"
  source = data.local_file.deploy-zip.filename
}
# cloudwatch log group
resource "aws_cloudwatch_log_group" "lambda_function_log" {
  name = "/aws/lambda/${aws_lambda_function.lambda.function_name}"

  tags = {
    Environment = "TESTING"
    Application = "TDSA"
  }
}


# deployment_zip_file.
data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "../"
  output_path = "../temp/lambda.zip"
  excludes    = [".gitignore"]

}

# find local file deploy.zip | Note - This file is created during the run build.sh in the github action.
# The file gets created inside the containter running the action, gets uploaded to the bucket,
# then deletes when the container is shut down



# lambda policy 
resource "aws_iam_role_policy" "lambda_policy" {
  name   = "lambda_policy"
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.assume_lambda_policy.json
}


# lambda role
resource "aws_iam_role" "lambda_role" {
  name               = "lambda_role"
  assume_role_policy = data.aws_iam_policy_document.assume_lambda_role.json
}
