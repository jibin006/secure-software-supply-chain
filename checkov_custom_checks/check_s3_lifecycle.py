from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class S3LifecyclePolicyCheck(BaseResourceCheck):
    def __init__(self):
        name = "Ensure S3 bucket has a lifecycle policy attached"
        id = "CKV_CUSTOM_S3_1"
        supported_resources = ["aws_s3_bucket"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id,
                         categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        lifecycle = conf.get("lifecycle_rule", [])
        
        if lifecycle and lifecycle != [[]]:
            return CheckResult.PASSED
        return CheckResult.FAILED

check = S3LifecyclePolicyCheck()
