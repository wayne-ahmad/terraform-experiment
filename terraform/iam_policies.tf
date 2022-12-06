
data "aws_iam_policy_document" "assume_lambda_role" {
  statement {
    sid     = "AssumeRole"
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }
  }
}


data "aws_iam_policy_document" "assume_lambda_policy" {
  statement {
    sid = "lambdaTriggerAction"
    actions = [
      "logs:*",
      "s3:GetObject",
      "s3:putObject",
      "s3:ListBucket",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage"
    ]
    effect    = "Allow"
    resources = ["*"]
  }
}

