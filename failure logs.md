FAILURE LOG — 2026-05-07

What broke:
CKV_CUSTOM_S3_1 failed on compliant bucket that had a lifecycle 
configuration attached.

What I expected to happen:
Check passes on any bucket with lifecycle configuration present.

What actually happened:
Check returned FAILED because it looked for lifecycle_rule inline 
attribute on aws_s3_bucket which does not exist in provider v4+.

Root cause:
AWS provider v4 moved lifecycle configuration to a separate resource 
aws_s3_bucket_lifecycle_configuration. The inline lifecycle_rule block 
was deprecated. My check targeted the old structure.

What assumption was wrong:
I assumed Terraform resource structure is stable across provider 
versions. It is not — provider major versions can restructure resource 
attributes entirely.

What I changed:
Changed supported_resources to aws_s3_bucket_lifecycle_configuration 
and validated enabled rules within that resource directly.

The trade-off or residual risk:
Check is now silent when lifecycle resource is completely absent — 
depends on CKV2_AWS_61 to catch that case. If Prisma Cloud changes 
CKV2_AWS_61 behavior, enforcement silently degrades.

What I monitor for:
Pin Checkov version in CI. Keep a non-compliant fixture that must 
always fail — if it passes after a Checkov upgrade, investigate 
immediately.


FAILURE LOG — 2026-05-07
Entry 1 — Checkov custom check not loading

What broke:
CKV_CUSTOM_S3_1 did not appear in scan output; no failures or passes recorded.

What I expected to happen:
Checkov loads all .py files in the external checks directory and evaluates them automatically.

What actually happened:
Checkov silently ignored the custom check; scan executed without registering the rule.

Root cause:
Missing __init__.py — Checkov imports the directory as a Python module, not as loose files.

What assumption was wrong:
I assumed Checkov dynamically scans files in a folder; in reality it relies on Python module import semantics.

What I changed:
Added __init__.py to the custom checks directory so Checkov can import and register the check.

The trade-off or residual risk:
Any structural issue (bad import, syntax error) in the module will silently prevent check registration without explicit failure.

What I monitor for:
Verify custom check IDs appear in every scan output; maintain a failing fixture to ensure the check is actively evaluated.

FAILURE LOG — 2026-05-07
Entry 2 — Wrong Rego path (silent pass)

What broke:
OPA policy returned 0 tests and 0 failures against a security group with 0.0.0.0/0 on port 22.

What I expected to happen:
Policy should detect the open SSH rule and fail the evaluation.

What actually happened:
No rules evaluated; Conftest returned success despite insecure configuration.

Root cause:
Incorrect JSON path input.resource.aws_security_group[_] — does not exist in Terraform plan structure.

What assumption was wrong:
I assumed Terraform plan JSON mirrors HCL resource structure; in reality, OPA evaluates the resolved execution plan under planned_values or resource_changes.

What I changed:
Updated policy to reference input.planned_values.root_module.resources[_] and correct nested attributes.

The trade-off or residual risk:
Policy is tightly coupled to plan JSON schema; changes in Terraform output structure or using resource_changes instead of planned_values can break detection silently.

What I monitor for:
Maintain a known-bad SG fixture; if it ever passes, treat as policy regression. Periodically validate policy against both planned_values and resource_changes.

FAILURE LOG — 2026-05-07
Entry 3 — (Already provided, correct)
FAILURE LOG — 2026-05-07
Entry 4 — Conftest namespace mismatch (silent pass)

What broke:
OPA policy produced 0 tests and 0 failures even with correct logic and valid plan JSON.

What I expected to happen:
Conftest should automatically evaluate all .rego files in the policies directory.

What actually happened:
Policy was ignored because it was under package terraform.security, while Conftest defaults to package main.

Root cause:
Namespace mismatch — Conftest does not evaluate non-main packages unless --namespace is explicitly provided.

What assumption was wrong:
I assumed policy discovery is package-agnostic; in reality, evaluation is namespace-scoped.

What I changed:
Standardized on explicit namespace usage (--namespace terraform.security) in CI.

The trade-off or residual risk:
If the namespace flag is omitted or misconfigured in CI, all policies silently stop executing while pipeline remains green.

What I monitor for:
CI must fail on known-bad fixtures; additionally log rule counts (conftest test -o json) to detect “0 tests” scenarios.

FAILURE LOG — 2026-05-07
Entry 5 — Terraform provider binary committed to Git history

What broke:
Push to GitHub rejected due to 628MB provider binary exceeding size limit.

What I expected to happen:
.gitignore would prevent .terraform/ from being committed.

What actually happened:
Binary was already tracked before .gitignore was added; Git continued tracking it and propagated it into history.

Root cause:
.gitignore only affects untracked files; once committed, files persist in history unless explicitly removed.

What assumption was wrong:
I assumed .gitignore retroactively removes tracked files; it does not.

What I changed:
Used git filter-repo to remove .terraform/ from entire history and force-pushed cleaned repo.

The trade-off or residual risk:
History rewrite disrupts collaborators and requires force push; future mistakes can reintroduce large artifacts if .gitignore discipline is not enforced.

What I monitor for:
Run git rev-list --objects --all checks for large files; enforce pre-commit hooks or CI checks to block .terraform/.

FAILURE LOG — 2026-05-07
Entry 6 — Checkov encryption check interpretation (CKV_AWS_19 vs CKV_AWS_145)

What broke:
CKV_AWS_19 passed despite no explicit encryption block; expectation was failure.

What I expected to happen:
Bucket without encryption configuration should fail security checks.

What actually happened:
CKV_AWS_19 passed because AWS enables SSE-S3 by default; CKV_AWS_145 failed correctly for missing KMS encryption.

Root cause:
Mismatch between tool logic and evolving cloud provider defaults.

What assumption was wrong:
I assumed absence of explicit encryption equals non-compliance; provider defaults can satisfy certain controls implicitly.

What I changed:
Used CKV_AWS_145 (KMS enforcement) as the real control signal instead of relying on CKV_AWS_19.

The trade-off or residual risk:
Default SSE-S3 provides encryption but lacks key management control, auditability, and fine-grained access policies compared to KMS.

What I monitor for:
Ensure KMS-specific checks are enforced; periodically review provider defaults and update policy expectations accordingly.




CKV_AWS_19 passed despite no explicit encryption block in Terraform. Root cause: AWS S3 now enables SSE-S3 by default since 2023. Checkov treats default encryption as compliant. The gap: default SSE-S3 is not KMS — CKV_AWS_145 correctly fails because KMS encryption requires explicit configuration. Learning: tool output must be understood against provider behavior, not just accepted


Custom check CKV_CUSTOM_S3_1 did not load on first run. Root cause: missing __init__.py in the external checks directory — Checkov requires the folder to be a Python package for check registration. 
Fix: added __init__.py. Learning: external check directories are not file-scanned, they are imported as Python modules.


CKV_CUSTOM_S3_1 failed on compliant bucket. Root cause: check used lifecycle_rule inline attribute which does not exist in AWS provider v4+ — lifecycle is now a separate resource aws_s3_bucket_lifecycle_configuration. Fix: changed supported_resources to target the lifecycle resource directly and validate enabled rules within it. Learning: Checkov custom checks must be written against the provider version in use — v3 and v4 Terraform AWS provider have different resource structures for the same configuration.


Wrong Rego path input.resource.aws_security_group[_] produced 0 tests, 0 failures against a security group with 0.0.0.0/0 on port 22. Root cause: path does not exist in plan JSON — conftest found no matching data, evaluated no rules, and returned success. This is the silent pass failure mode. In production this gate would never fire on any security group misconfiguration while appearing to work correctly.


Correct Rego policy produced 0 tests against valid plan JSON. Root cause: conftest only evaluates rules in package main by default — custom package namespaces like terraform.security are silently ignored without --namespace flag. The policy was correct, the data was correct, the gate was broken. If shipped without --namespace, this gate would never fire on any violation while showing 0 failures. Fix: either change package to main or always pass --namespace flag explicitly in CI.


Committed 628MB Terraform provider binary to git history. Root cause: .gitignore was created after terraform init ran and after the first commit — files already tracked by git are not affected by .gitignore. Fix: git filter-branch to purge from history, force push. Learning: .gitignore must exist before terraform init. For any Terraform repo, the correct order is: create repo, add .gitignore with .terraform/ pattern, then run terraform init. Never the reverse.



FAILURE LOG — 2026-05-09

What broke:
Lambda failed with AttributeError when trying to catch s3.exceptions.NoSuchPublicAccessBlockConfiguration during get_public_access_block call.

What I expected to happen:
When a bucket has no public access block, the SDK would raise a typed exception NoSuchPublicAccessBlockConfiguration that I could catch directly via s3.exceptions.

What actually happened:
The Lambda crashed because that exception class does not exist in botocore; the error was not caught and the evaluation logic failed before generating findings.

Root cause:
S3 get_public_access_block returns a generic ClientError with error code "NoSuchPublicAccessBlockConfiguration" instead of a modeled exception class, so botocore does not expose it under s3.exceptions.

What assumption was wrong:
I assumed all AWS API errors are exposed as typed exceptions in client.exceptions.*; in reality, many S3 errors are only surfaced as generic ClientError with string-based error codes.

What I changed:
Replaced the specific exception catch with botocore.exceptions.ClientError and added conditional logic to check e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration".

Trade-off or residual risk:
String-based error handling is brittle—if AWS changes error codes or introduces variations, the detection logic may silently fail or misclassify conditions.

What I monitor for:
Add a test case with a bucket missing public access block that must always produce a finding; log and alert on any unexpected ClientError codes to detect API behavior drift early.
