CKV_AWS_19 passed despite no explicit encryption block in Terraform. Root cause: AWS S3 now enables SSE-S3 by default since 2023. Checkov treats default encryption as compliant. The gap: default SSE-S3 is not KMS — CKV_AWS_145 correctly fails because KMS encryption requires explicit configuration. Learning: tool output must be understood against provider behavior, not just accepted


Custom check CKV_CUSTOM_S3_1 did not load on first run. Root cause: missing __init__.py in the external checks directory — Checkov requires the folder to be a Python package for check registration. 
Fix: added __init__.py. Learning: external check directories are not file-scanned, they are imported as Python modules.


CKV_CUSTOM_S3_1 failed on compliant bucket. Root cause: check used lifecycle_rule inline attribute which does not exist in AWS provider v4+ — lifecycle is now a separate resource aws_s3_bucket_lifecycle_configuration. Fix: changed supported_resources to target the lifecycle resource directly and validate enabled rules within it. Learning: Checkov custom checks must be written against the provider version in use — v3 and v4 Terraform AWS provider have different resource structures for the same configuration.


Wrong Rego path input.resource.aws_security_group[_] produced 0 tests, 0 failures against a security group with 0.0.0.0/0 on port 22. Root cause: path does not exist in plan JSON — conftest found no matching data, evaluated no rules, and returned success. This is the silent pass failure mode. In production this gate would never fire on any security group misconfiguration while appearing to work correctly.


Correct Rego policy produced 0 tests against valid plan JSON. Root cause: conftest only evaluates rules in package main by default — custom package namespaces like terraform.security are silently ignored without --namespace flag. The policy was correct, the data was correct, the gate was broken. If shipped without --namespace, this gate would never fire on any violation while showing 0 failures. Fix: either change package to main or always pass --namespace flag explicitly in CI.


Committed 628MB Terraform provider binary to git history. Root cause: .gitignore was created after terraform init ran and after the first commit — files already tracked by git are not affected by .gitignore. Fix: git filter-branch to purge from history, force push. Learning: .gitignore must exist before terraform init. For any Terraform repo, the correct order is: create repo, add .gitignore with .terraform/ pattern, then run terraform init. Never the reverse.
