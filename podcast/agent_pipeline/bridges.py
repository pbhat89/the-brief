"""Fail-closed bridges to existing editorial/audio/publishing contracts.

No credentials or provider configuration are embedded in the public repository.
"""
from pathlib import Path
import hashlib
import json
import subprocess


def validate_editorial(repo, audit_path):
    repo=Path(repo).resolve(); audit_path=Path(audit_path).resolve()
    if not audit_path.is_file(): raise ValueError('Private editorial audit missing')
    subprocess.run(['node',str(repo/'podcast/validate-editorial.mjs'),'--audit',str(audit_path)],cwd=repo,check=True,capture_output=True,text=True,timeout=60)
    return {'status':'passed','audit_sha256':hashlib.sha256(audit_path.read_bytes()).hexdigest()}


def validate_voice(validator, script, profile, contract):
    paths=[Path(p).resolve() for p in (validator,script,profile,contract)]
    if not all(p.is_file() for p in paths): raise ValueError('Approved voice contract input missing')
    subprocess.run(['python',str(paths[0]),'--script',str(paths[1]),'--profile',str(paths[2]),'--contract',str(paths[3])],check=True,capture_output=True,text=True,timeout=60)
    return {'status':'passed','contract_sha256':hashlib.sha256(paths[3].read_bytes()).hexdigest()}


def publish_verified(client, *, edition_id, audio_path, metadata, allow_publish=False):
    """Client implements lookup(id), upload(id,bytes,metadata), readback(receipt).

    A timed-out upload is never automatically repeated. The caller reconciles the
    same edition ID on its next invocation. The client owns authorized transport.
    """
    if not allow_publish: raise ValueError('Publication is disabled for comparison runs')
    data=Path(audio_path).read_bytes(); sha=hashlib.sha256(data).hexdigest()
    prior=client.lookup(edition_id)
    if prior is None:
        try: receipt=client.upload(edition_id,data,{**metadata,'sha256':sha})
        except TimeoutError:
            receipt=client.lookup(edition_id)
            if receipt is None: raise RuntimeError('Upload outcome uncertain; reconcile before retry') from None
    else: receipt=prior
    if receipt.get('sha256')!=sha: raise ValueError('Existing edition differs; never overwrite')
    stored=client.readback(receipt)
    if hashlib.sha256(stored).hexdigest()!=sha: raise ValueError('Stored bytes mismatch')
    return {'edition_id':edition_id,'sha256':sha,'bytes':len(data),'published':True,'readback_verified':True,'playback_verified':False}
