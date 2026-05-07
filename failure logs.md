CKV_AWS_19 passed despite no explicit encryption block in Terraform. Root cause: AWS S3 now enables SSE-S3 by default since 2023. Checkov treats default encryption as compliant. The gap: default SSE-S3 is not KMS — CKV_AWS_145 correctly fails because KMS encryption requires explicit configuration. Learning: tool output must be understood against provider behavior, not just accepted


Custom check CKV_CUSTOM_S3_1 did not load on first run. Root cause: missing __init__.py in the external checks directory — Checkov requires the folder to be a Python package for check registration. 
Fix: added __init__.py. Learning: external check directories are not file-scanned, they are imported as Python modules.


CKV_CUSTOM_S3_1 failed on compliant bucket. Root cause: check used lifecycle_rule inline attribute which does not exist in AWS provider v4+ — lifecycle is now a separate resource aws_s3_bucket_lifecycle_configuration. Fix: changed supported_resources to target the lifecycle resource directly and validate enabled rules within it. Learning: Checkov custom checks must be written against the provider version in use — v3 and v4 Terraform AWS provider have different resource structures for the same configuration.
