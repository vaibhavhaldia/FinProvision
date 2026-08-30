resource "aws_iam_role" "pipeline" {
  name = "${var.service_name}-pipeline-role-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })

  tags = {
    Service   = var.service_name
    ManagedBy = "tradeforge"
  }
}

resource "aws_iam_role_policy" "pipeline_s3" {
  name = "${var.service_name}-s3-policy"
  role = aws_iam_role.pipeline.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/${var.service_name}/*"
          # Scoped to service prefix ONLY — never wildcard
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["kms:GenerateDataKey", "kms:Decrypt"]
        Resource = var.kms_key_arn != null ? [var.kms_key_arn] : []
      }
    ]
  })
}