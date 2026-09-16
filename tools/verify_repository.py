"""Standard-library import-integrity checks, not a scientific reproduction."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','__pycache__','.pytest_cache','.venv','venv','build','dist'}
FORBIDDEN_SUFFIXES={'.pem','.key','.p12','.pfx','.safetensors','.pt','.pth','.ckpt','.bin','.pyc','.zip','.jsonl'}
PATTERNS={
    'private key':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'AWS access key':re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'GitHub token':re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b'),
    'service key':re.compile(r'\b(?:sk-proj-|sk-ant-|hf_)[A-Za-z0-9_-]{24,}\b'),
    'credential assignment':re.compile(r'''(?im)["']?(?:api_key|access_token|password|client_secret)["']?\s*[:=]\s*["'][A-Za-z0-9_+/=.-]{16,}["']'''),
}

def main():
    errors=[]; manifest=json.loads((ROOT/'reproducibility/supplement_manifest.json').read_text())
    for row in manifest['included']:
        p=(ROOT/row['repository_path']).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file():
            errors.append(f"Missing/unsafe import path: {row['repository_path']}"); continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=row['repository_sha256']:
            errors.append(f"Imported fingerprint mismatch: {row['repository_path']}")
        if row['source_sha256']!=row['repository_sha256'] and row['transformation']=='none':
            errors.append(f"Unrecorded import transformation: {row['repository_path']}")
    counts={'python':0,'json':0,'files':0}
    for p in ROOT.rglob('*'):
        rel=p.relative_to(ROOT)
        if any(part in SKIP or part.endswith('.egg-info') for part in rel.parts) or not p.is_file(): continue
        counts['files']+=1
        if p.suffix.lower() in FORBIDDEN_SUFFIXES or p.name.startswith('.env') or rel.parts[0] in {'private','data','artifacts','results'}:
            errors.append(f'Forbidden release file: {rel}')
        if p.stat().st_size>10*1024*1024: errors.append(f'Oversized release file: {rel}')
        try: text=p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            errors.append(f'Unexpected binary file: {rel}'); continue
        try:
            if p.suffix=='.py': ast.parse(text,filename=str(rel)); counts['python']+=1
            elif p.suffix=='.json': json.loads(text); counts['json']+=1
            elif p.suffix=='.toml': tomllib.loads(text)
        except (SyntaxError,ValueError) as e: errors.append(f'Parse error: {rel}: {e}')
        for label,pattern in PATTERNS.items():
            if pattern.search(text): errors.append(f'Potential {label}: {rel}')
        if p.suffix in {'.json','.md','.yaml'} and re.search(r'[A-Za-z]:[\\/]+Users[\\/]+',text):
            errors.append(f'Local user path: {rel}')
    if errors:
        print('\n'.join(errors)); return 1
    print(json.dumps({'passed':True,'imported_files':len(manifest['included']),
                      'excluded_bytecode':len(manifest['excluded']),'checked':counts,
                      'scope':'File integrity, syntax and common release hazards only.'},indent=2))
    return 0

if __name__=='__main__': sys.exit(main())
