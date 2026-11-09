"""Exact public-source URLs; never redact a URL and pretend it was the request."""
import ipaddress
import re
from urllib.parse import urlsplit, unquote

def public_source_url(value):
    if not isinstance(value,str) or len(value)>2048:return None
    try:
        p=urlsplit(value);host=p.hostname
        if p.scheme not in ('https','http') or not host or p.username or p.password or p.query or p.fragment:return None
        if host=='localhost' or '.' not in host or host.endswith(('.local','.internal')):return None
        try:
            if not ipaddress.ip_address(host).is_global:return None
        except ValueError:pass
        path=unquote(p.path)
        if any(c in path for c in ('\\','\x00','\r','\n')):return None
        if '@' in path and not (host.lower() in ('youtube.com','www.youtube.com') and re.fullmatch(r'/@[A-Za-z0-9_.-]+(?:/(?:videos|streams|live|featured))?/?',path)):return None
        for segment in path.split('/'):
            # Reject credential/login route components, not innocent words such as secretary.
            if re.search(r'(^|[-_.=])(token|secret|password|auth|login|session)([-_.=]|$)',segment,re.I):return None
            if len(segment)>512 or (len(segment)>100 and '-' not in segment):return None
        return value
    except (ValueError,TypeError):return None
