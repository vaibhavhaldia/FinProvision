output "bucket_name" { value = aws_s3_bucket.data_lake.bucket }
output "bucket_arn"  { value = aws_s3_bucket.data_lake.arn }
output "kms_key_arn" { value = var.kms_enabled ? aws_kms_key.s3_key[0].arn : null }