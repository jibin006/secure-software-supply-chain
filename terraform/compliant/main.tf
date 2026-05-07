resource "aws_s3_bucket" "compliant" {
  bucket = "compliant-bucket"
}

resource "aws_s3_bucket_lifecycle_configuration" "compliant_lifecycle" {
  bucket = aws_s3_bucket.compliant.id

  rule {
    id     = "expire-old-objects"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}
