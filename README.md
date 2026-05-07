# secure-cicd-pipeline


I built a custom Checkov check CKV_CUSTOM_S3_1 enforcing S3 lifecycle policy, it failed to load on first run because the external checks directory was missing __init__.py, I fixed it by adding the file to make the folder a Python package, the trade-off I accepted is inline suppression can bypass this check, and I monitor for suppression accumulation by scanning for checkov:skip comments in CI.


I built a custom Checkov check CKV_CUSTOM_S3_1 enforcing S3 lifecycle policy, it broke because the check targeted lifecycle_rule inline attribute which does not exist in AWS provider v4+ — lifecycle is now a separate resource type, I fixed it by changing supported_resources to aws_s3_bucket_lifecycle_configuration and validating enabled rules within it, the trade-off I accepted is the check is now silent when the lifecycle resource is completely absent and I depend on CKV2_AWS_61 to catch that case, and I monitor for upstream Checkov rule behavior changes via pinned Checkov versions in CI.


Wrong Rego path input.resource.aws_security_group[_] assumes HCL structure maps directly to plan JSON. It does not. Plan JSON wraps resources under planned_values.root_module.resources[] with type, name, and values fields. The wrong path evaluates against a key that does not exist, returns no results, and silently passes. If shipped to production this gate would never fire on any security group misconfiguration.
