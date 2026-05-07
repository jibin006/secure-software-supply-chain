Custom check CKV_CUSTOM_S3_1 did not load on first run. Root cause: missing __init__.py in the external checks directory — Checkov requires the folder to be a Python package for check registration. 
Fix: added __init__.py. Learning: external check directories are not file-scanned, they are imported as Python modules.
