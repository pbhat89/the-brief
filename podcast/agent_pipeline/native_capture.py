"""Preserve external tool-call receipts. Never invokes or impersonates a connector."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from .audit import verify_private_path
from .native_bridge import canonical,digest,identifier,NativeBridgeError
from .native_urls import public_source_url as _public_url


def save_receipt(directory,envelope):
    root=Path(directory).resolve();verify_private_path(root)
    if set(envelope)!={'request_url','started_at','observed_at','tool_result'}:
        raise NativeBridgeError('Exact capture envelope required')
    url=envelope['request_url']
    if url is None or _public_url(url)!=url:raise NativeBridgeError('Public exact requested URL required')
    start=datetime.fromisoformat(envelope['started_at'].replace('Z','+00:00'))
    end=datetime.fromisoformat(envelope['observed_at'].replace('Z','+00:00'))
    if start.tzinfo is None or end.tzinfo is None or end<start:raise NativeBridgeError('Invalid wrapper times')
    if not isinstance(envelope['tool_result'],dict):raise NativeBridgeError('Original tool result object required')
    receipt_id=digest(envelope)
    result_hash=digest(envelope['tool_result'])
    path=root/(receipt_id+'.receipt.json')
    encoded=canonical(envelope).encode()
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:
        if path.is_symlink() or path.read_bytes()!=encoded:raise NativeBridgeError('Receipt conflict')
    else:
        with os.fdopen(fd,'wb') as stream:
            stream.write(encoded);stream.flush();os.fsync(stream.fileno())
    return dict(receipt_id=receipt_id,receipt_file=str(path),tool_result_sha256=result_hash,
                actual_tool_attestation=False)


def manifest(directory,receipt_id,driver_id,tool_ref,outcome):
    """The caller must review the original result before declaring opened/failed.

    Ref containment prevents invented reference IDs, but does not prove semantic
    success or authenticate an external service. Root may review the raw receipt.
    """
    import re
    root=Path(directory).resolve();verify_private_path(root)
    if not re.fullmatch('[0-9a-f]{64}',receipt_id):raise NativeBridgeError('Invalid receipt ID')
    identifier(driver_id);identifier(tool_ref)
    if outcome not in ('opened','failed','unknown'):raise NativeBridgeError('Explicit outcome required')
    path=root/(receipt_id+'.receipt.json');verify_private_path(path)
    envelope=json.loads(path.read_text(encoding='utf-8'))
    if digest(envelope)!=receipt_id:raise NativeBridgeError('Receipt hash mismatch')
    original=canonical(envelope['tool_result'])
    if tool_ref not in original:raise NativeBridgeError('Reference not present in original tool result')
    return {'manifest_id':receipt_id,'driver_id':driver_id,'entries':[{
        'tool_ref':tool_ref,'tool_name':'chat_search_web_run','operation':{'opened':'open','failed':'open_failed','unknown':'open_unknown'}[outcome],
        'url':envelope['request_url'],'basis':'driver_observed','started_at':envelope['started_at'],
        'observed_at':envelope['observed_at'],'tool_result_sha256':digest(envelope['tool_result'])}]}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True)
    sub=p.add_subparsers(dest='command',required=True);sub.add_parser('save')
    m=sub.add_parser('manifest')
    for name in ('receipt-id','driver-id','tool-ref','outcome'):m.add_argument('--'+name,required=True)
    a=vars(p.parse_args());command=a.pop('command')
    if command=='save':result=save_receipt(a['directory'],json.load(sys.stdin))
    else:result=manifest(**a)
    print(canonical(result))
if __name__=='__main__':main()
