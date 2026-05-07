resource "aws_s3_bucket" "non_compliant" {
  bucket = "non-compliant-bucket"
}
# No lifecycle configuration
