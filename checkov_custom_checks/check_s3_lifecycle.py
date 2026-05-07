from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class S3LifecyclePolicyCheck(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 bucket has an enabled lifecycle policy with expiration or transition"
        id = "CKV_CUSTOM_S3_1"
        supported_resources = ["aws_s3_bucket_lifecycle_configuration"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        rules = conf.get("rule")

        if not rules:
            return CheckResult.FAILED

        if isinstance(rules[0], list):
            rules = rules[0]

        for rule in rules:
            if not isinstance(rule, dict):
                continue

            status = rule.get("status", [""])[0]
            expiration = rule.get("expiration")
            transition = rule.get("transition")

            if status == "Enabled" and (expiration or transition):
                return CheckResult.PASSED

        return CheckResult.FAILED

check = S3LifecyclePolicyCheck()
