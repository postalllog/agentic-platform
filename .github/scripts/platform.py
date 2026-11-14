#!/usr/bin/env python3
"""Developer CLI: validate, scaffold, build and run AgentCore CodeZip workloads."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKLOAD_ROOTS = (ROOT / "workloads" / "agents", ROOT / "workloads" / "mcp-servers")
VALID_NAME = re.compile(r"^[a-z][a-z0-9-]{1,39}$")


def resolve_workload(value):
    candidate = (ROOT / value).resolve()
    if candidate.parent not in WORKLOAD_ROOTS:
        raise ValueError('Expected a direct child of workloads/agents or workloads/mcp-servers')
    if not candidate.is_dir():
        raise ValueError(f'Missing workload directory: {candidate}')
    return candidate


def read_manifest(folder):
    path = folder / 'agent.yaml'
    if not path.is_file():
        raise ValueError(f'Missing {path}')
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Manifest must be a YAML mapping')
    return data


def validate(folder):
    data = read_manifest(folder)
    kind = 'Agent' if folder.parent.name == 'agents' else 'MCPServer'
    assert data.get('apiVersion') == 'postalllog.ai/v1', 'Unsupported apiVersion'
    assert data.get('kind') == kind, f'Expected kind {kind}'
    name = data['metadata']['name']
    assert name == folder.name and VALID_NAME.fullmatch(name), 'Invalid workload name'
    assert isinstance(data['metadata'].get('owner'), str) and data['metadata']['owner'], 'Missing owner'
    runtime = data['spec']['runtime']
    assert runtime['deployment'] == 'code_zip', 'Only code_zip is supported'
    assert runtime['protocol'] in ('HTTP', 'MCP', 'A2A', 'AGUI'), 'Unknown protocol'
    if kind == 'MCPServer':
        assert runtime['protocol'] == 'MCP', 'MCPServer requires MCP'
    entry = runtime['entrypoint']
    assert entry == 'main.py' and (folder / entry).is_file(), 'Entry point must be main.py'
    assert (folder / 'requirements.txt').is_file(), 'Missing requirements'
    assert data['spec']['exposure']['authentication'] == 'IAM', 'Only IAM inbound is supported by this template'
    model_arns = data['spec'].get('models', {}).get('arns', [])
    assert isinstance(model_arns, list) and all(isinstance(x, str) and x.startswith('arn:aws:bedrock:') for x in model_arns), 'Use explicit Bedrock ARNs'
    caps = data['spec'].get('capabilities', {})
    assert not any(caps.get(x, False) for x in ('memory', 'browser', 'code_interpreter')), 'Optional capabilities not yet provisioned by this release'
    print(f'OK {folder.relative_to(ROOT)} ({runtime["protocol"]})')
    return data


def validate_all():
    for parent in WORKLOAD_ROOTS:
        for path in sorted(parent.iterdir()):
            if path.is_dir() and (path / 'agent.yaml').exists():
                validate(path)


def scaffold(kind, name):
    if not VALID_NAME.fullmatch(name):
        raise ValueError('Name must be lowercase kebab-case, 2-40 characters')
    parent = WORKLOAD_ROOTS[0] if kind == 'agent' else WORKLOAD_ROOTS[1]
    dest = parent / name
    if dest.exists():
        raise FileExistsError(dest)
    source = WORKLOAD_ROOTS[0] / 'hello-world' if kind == 'agent' else WORKLOAD_ROOTS[1] / 'hello-tools'
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
    manifest = read_manifest(dest)
    manifest['metadata']['name'] = name
    (dest / 'agent.yaml').write_text(yaml.safe_dump(manifest, sort_keys=False), encoding='utf-8')
    print(f'Created {dest.relative_to(ROOT)}. Edit main.py and agent.yaml.')


def build(folder, output_dir):
    validate(folder)
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / 'agent.zip'
    with tempfile.TemporaryDirectory(prefix='agentcore-build-') as tmp:
        tmp = Path(tmp)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '-r', str(folder/'requirements.txt'), '--target', str(tmp), '--platform', 'manylinux2014_aarch64', '--python-version', '3.13', '--implementation', 'cp', '--abi', 'cp313', '--only-binary=:all:'], check=True)
        shutil.copy2(folder/'main.py', tmp/'main.py')
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for file in sorted(tmp.rglob('*')):
                if file.is_file():
                    rel = file.relative_to(tmp).as_posix()
                    if '/__pycache__/' not in f'/{rel}/' and not rel.endswith('.pyc'):
                        z.write(file, rel)
    print(f'Built {archive} ({archive.stat().st_size} bytes, SHA256={hashlib.sha256(archive.read_bytes()).hexdigest()})')
    if archive.stat().st_size > 250*1024*1024:
        raise ValueError('CodeZip exceeds 250 MiB; reduce dependencies')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('new'); p.add_argument('kind', choices=['agent', 'mcp-server']); p.add_argument('name')
    p = sub.add_parser('validate'); p.add_argument('workload')
    sub.add_parser('validate-all')
    p = sub.add_parser('build'); p.add_argument('workload'); p.add_argument('--output-dir', default='dist')
    p = sub.add_parser('dev'); p.add_argument('workload')
    args = parser.parse_args()
    try:
        if args.command == 'new': scaffold(args.kind, args.name)
        elif args.command == 'validate-all': validate_all()
        elif args.command == 'validate': validate(resolve_workload(args.workload))
        elif args.command == 'build': build(resolve_workload(args.workload), args.output_dir)
        elif args.command == 'dev':
            folder = resolve_workload(args.workload)
            validate(folder)
            subprocess.run([sys.executable, 'main.py'], cwd=folder, check=True)
    except (ValueError, AssertionError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
