# secure-cicd-pipeline


I built a custom Checkov check CKV_CUSTOM_S3_1 enforcing S3 lifecycle policy, it failed to load on first run because the external checks directory was missing __init__.py, I fixed it by adding the file to make the folder a Python package, the trade-off I accepted is inline suppression can bypass this check, and I monitor for suppression accumulation by scanning for checkov:skip comments in CI.
