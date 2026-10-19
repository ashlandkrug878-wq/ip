#!/usr/bin/env python3
"""Check Study archive structure and references; not truth or rights verification."""
import hashlib
import json
import sys
from pathlib import Path

def validate(folder):
    root = Path(folder)
    data = json.loads((root / 'archive.json').read_text(encoding='utf-8'))
    errors = []
    tables = {'entities':'entity_id','claims':'claim_id','evidence':'evidence_id','events':'event_id','products':'product_id','accounts':'account_id','content_samples':'content_id','user_evidence':'user_evidence_id','images':'image_id','visual_analyses':'analysis_id','methods':'method_id','gaps':'gap_id'}
    if data.get('schema_version') == '1.1': tables['publications'] = 'publication_id'
    for key in ['schema_version','subject_id','cutoff_date','observed_at','markets','status','coverage','character_rules',*tables]:
        if key not in data: errors.append(f'missing top-level {key}')
    if data.get('schema_version') == '1.1':
        for key in ['revision','color_system','form_spec','head_face_profile','narrative_system','action_library','series_matrix','recognition_checks','audience_insights','repo_audit']:
            if key not in data: errors.append(f'missing v0.2 field {key}')
    ids = {}
    for table, key in tables.items():
        rows = data.get(table, [])
        if not isinstance(rows, list):
            errors.append(f'{table} must be array'); continue
        vals = [row.get(key) for row in rows]
        if None in vals or len(vals) != len(set(vals)): errors.append(f'{table}: missing or duplicate ID')
        ids[table] = set(vals)
    if data.get('subject_id') not in ids['entities']: errors.append('unknown root subject')
    refs = {'evidence_ids':'evidence','claim_ids':'claims','image_ids':'images','product_ids':'products','event_ids':'events','subject_ids':'entities','subject_id':'entities','image_id':'images','account_id':'accounts'}
    def walk(value):
        if isinstance(value, dict):
            for key, val in value.items():
                if key in refs and val is not None:
                    for item in val if isinstance(val, list) else [val]:
                        if item not in ids[refs[key]]: errors.append(f'unknown {key}: {item}')
                walk(val)
        elif isinstance(value, list):
            for item in value: walk(item)
    walk(data)
    required = ['claim_id','subject_id','predicate','value','unit','market','valid_time','observed_at','evidence_ids','information_type','confidence','limitations']
    for c in data.get('claims', []):
        for key in required:
            if key not in c: errors.append(f'{c.get("claim_id")}: missing {key}')
        if c.get('information_type') not in {'fact','self_report','inference','hypothesis'}: errors.append('invalid information_type')
        if c.get('confidence') not in {'high','medium','low'}: errors.append('invalid confidence')
        if not c.get('evidence_ids'): errors.append(f'{c.get("claim_id")}: no evidence')
    for im in data.get('images', []):
        if im.get('save_status') == 'saved':
            rel = im.get('local_path')
            p = (root / rel).resolve() if rel else None
            if not p or not p.is_relative_to(root.resolve()) or not p.is_file(): errors.append(f'{im.get("image_id")}: missing or invalid saved path')
            elif hashlib.sha256(p.read_bytes()).hexdigest() != im.get('sha256'): errors.append(f'{im.get("image_id")}: checksum mismatch')
    for pal in data.get('color_system', []):
        for color in pal.get('colors', []):
            for key in ['role','scope','value_basis','image_ids','sample_method','uncertainty']:
                if key not in color: errors.append(f'color missing {key}')
            val = color.get('hex') or color.get('hex_preview')
            if val is not None and (len(val) != 7 or val[0] != '#' or any(c not in '0123456789abcdefABCDEF' for c in val[1:])): errors.append('invalid hex preview')
    if data.get('status') not in {'in_progress','partial','complete'}: errors.append('invalid status')
    if data.get('status') == 'complete':
        for name in [*'ABCDEFGHIJKL','visuals','prompts']:
            if data.get('coverage', {}).get(name, {}).get('status') != 'complete': errors.append(f'incomplete module {name}')
    return errors

if __name__ == '__main__':
    try: errors = validate(sys.argv[1])
    except (OSError, ValueError, IndexError, TypeError, AttributeError) as e:
        print(f'ERROR: {e}'); sys.exit(2)
    if errors:
        print('\n'.join('ERROR: '+e for e in errors)); sys.exit(1)
    print('PASS: structure, identifiers, references and saved-image hashes; facts and rights require review.')
