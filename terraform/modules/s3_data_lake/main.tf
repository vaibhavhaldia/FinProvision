resource "aws_kms_key" "s3_key" {
  count               = var.kms_enabled ? 1 : 0
  description         = "${var.service_name} S3 encryption key"
  enable_key_rotation = true   # SOX requirement — annual rotation

  tags = {
    Service     = var.service_name
    SOXRelevant = tostring(var.sox_relevant)
    ManagedBy   = "tradeforge"
  }
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.service_name}-data-lake-${var.env}"

  tags = {
    Service         = var.service_name
    Environment     = var.env
    DataClass       = var.data_classification
    SOXRelevant     = tostring(var.sox_relevant)
    ManagedBy       = "tradeforge"
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"    # Required for SOX audit trail
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_enabled ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_enabled ? aws_kms_key.s3_key[0].arn : null
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket                  = aws_s3_bucket.data_lake.id
  block_public_acls       = true    # ALWAYS — no exceptions
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}