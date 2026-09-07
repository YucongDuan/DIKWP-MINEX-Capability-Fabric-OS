from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from minexfabric.demo import demo_catalog, demo_intent, run_demo
from minexfabric.lease import create_lease
from minexfabric.models import CapabilityManifest, IntentSpec

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / 'validation' / 'schema-demo'
if TMP.exists():
    import shutil
    shutil.rmtree(TMP)
result = run_demo(TMP)

cases = [
    ('intent', ROOT/'schemas/intent.schema.json', demo_intent()),
    *[(f'capability:{x["capability_id"]}', ROOT/'schemas/capability.schema.json', CapabilityManifest.from_dict(x).to_dict()) for x in demo_catalog()],
    ('plan', ROOT/'schemas/plan.schema.json', json.loads((TMP/'plan.json').read_text())),
    ('receipt', ROOT/'schemas/receipt.schema.json', json.loads(Path(result['receipt']).read_text())),
    ('lease', ROOT/'schemas/lease.schema.json', create_lease('local-text-stats','local-core','consumer-a',b'a sufficiently long shared secret')),
]
checks=[]
for name,schema_path,value in cases:
    schema=json.loads(schema_path.read_text())
    errors=sorted(Draft202012Validator(schema).iter_errors(value), key=lambda e: list(e.path))
    checks.append({'case':name,'schema':schema_path.name,'valid':not errors,'errors':[e.message for e in errors]})
receipt={'validator':'jsonschema Draft 2020-12','checks':checks,'passed':all(x['valid'] for x in checks),'case_count':len(checks)}
(ROOT/'validation'/'SCHEMA_VALIDATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,indent=2,sort_keys=True))
raise SystemExit(0 if receipt['passed'] else 1)
