.PHONY: test demo audit model-check schema-check browser-smoke validate

test:
	PYTHONPATH=src python -m pytest -q

demo:
	PYTHONPATH=src python -m minexfabric demo --workspace validation/demo --reset

audit:
	python scripts/static_audit.py

model-check:
	python scripts/bounded_model_check.py --output validation/MINEX_1000_BOUNDED_MODEL_CHECK_RECEIPT_v1.0.0.json

schema-check:
	PYTHONPATH=src python scripts/validate_schemas.py

browser-smoke:
	python scripts/browser_smoke.py

validate: test audit model-check schema-check browser-smoke
