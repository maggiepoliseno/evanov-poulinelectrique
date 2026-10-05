#!/usr/bin/env python3
"""Copy the files of a read-only Nextcloud share into Final-Uploads/.

The portal (index.html, en/index.html) lists what is in
Final-Uploads/manifest.json under "Final uploads".

Usage: SHARE_URL=https://portail.poulinelectrique.com/s/<token> \
       python3 scripts/sync_final_uploads.py
Without SHARE_URL, the link in Final-Uploads/source.txt is used. With neither,
nothing changes.
"""
import base64
import json
import mimetypes
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'Final-Uploads')
FILES = os.path.join(OUT, 'Files')
MANIFEST = os.path.join(OUT, 'manifest.json')
# GitHub refuses files over 100 MB; bigger ones are linked to Nextcloud.
MAX_BYTES = 90 * 1000 * 1000
DAV = '{DAV:}'
PROPFIND = b'''<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:"><d:prop>
<d:getcontentlength/><d:getlastmodified/><d:getcontenttype/>
<d:getetag/><d:resourcetype/>
</d:prop></d:propfind>'''


def share_url():
    url = os.environ.get('SHARE_URL', '').strip()
    src = os.path.join(OUT, 'source.txt')
    if not url and os.path.exists(src):
        for line in open(src, encoding='utf-8'):
            line = line.strip()
            if line and not line.startswith('#'):
                url = line
                break
    return url


def parse_share(url):
    u = urllib.parse.urlparse(url)
    parts = [p for p in u.path.split('/') if p]
    if 's' not in parts or parts.index('s') + 1 >= len(parts):
        sys.exit(f'not a Nextcloud share link: {url}')
    token = parts[parts.index('s') + 1]
    prefix = '/'.join(parts[:parts.index('s')])
    prefix = prefix.replace('index.php', '').strip('/')
    base = f'{u.scheme}://{u.netloc}' + (f'/{prefix}' if prefix else '')
    return base, token


def request(method, url, token, body=None, depth=None):
    headers = {'User-Agent': 'evanov-final-uploads-sync'}
    if token:
        auth = base64.b64encode(f'{token}:'.encode()).decode()
        headers['Authorization'] = 'Basic ' + auth
    if depth is not None:
        headers['Depth'] = depth
        headers['Content-Type'] = 'application/xml'
    req = urllib.request.Request(url, data=body, headers=headers,
                                 method=method)
    return urllib.request.urlopen(req, timeout=120)


def listing(dav_root, token):
    """All files in the share: {relative path: properties}."""
    found, todo = {}, ['']
    root_path = urllib.parse.unquote(urllib.parse.urlparse(dav_root).path)
    while todo:
        rel = todo.pop()
        url = dav_root + urllib.parse.quote(rel)
        with request('PROPFIND', url, token, PROPFIND, '1') as r:
            tree = ET.fromstring(r.read())
        for resp in tree.findall(DAV + 'response'):
            href = resp.findtext(DAV + 'href') or ''
            path = urllib.parse.unquote(urllib.parse.urlparse(href).path)
            if not path.startswith(root_path):
                continue
            name = path[len(root_path):].strip('/')
            if name == rel.strip('/'):
                continue
            prop = resp.find(f'{DAV}propstat/{DAV}prop')
            if prop is None:
                continue
            is_dir = prop.find(f'{DAV}resourcetype/{DAV}collection')
            if is_dir is not None:
                todo.append(name + '/')
                continue
            if os.path.basename(name).startswith('.'):
                continue
            found[name] = {
                'size': int(prop.findtext(DAV + 'getcontentlength') or 0),
                'modified': prop.findtext(DAV + 'getlastmodified') or '',
                'type': prop.findtext(DAV + 'getcontenttype') or '',
                'etag': (prop.findtext(DAV + 'getetag') or '').strip('"'),
            }
    return found


def find_dav_root(base, token):
    """Newer Nextcloud: /public.php/dav/files/<token>/ (no login),
    older: /public.php/webdav/ with the token as the login.
    Returns the folder URL and the login to use."""
    code = None
    for root, login in ((f'{base}/public.php/dav/files/{token}/', None),
                        (f'{base}/public.php/webdav/', token)):
        try:
            with request('PROPFIND', root, login, PROPFIND, '0'):
                return root, login
        except urllib.error.HTTPError as e:
            code = e.code
    sys.exit(f'cannot read the share (HTTP {code}); it must be a'
             ' read-only link, not the upload-only one')


def iso(http_date):
    try:
        return parsedate_to_datetime(http_date).astimezone(
            timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    except (TypeError, ValueError):
        return ''


def main():
    url = share_url()
    if not url:
        print('no share link set - nothing to sync')
        return
    base, token = parse_share(url)
    dav_root, login = find_dav_root(base, token)
    remote = listing(dav_root, login)
    old = {}
    if os.path.exists(MANIFEST):
        for it in json.load(open(MANIFEST, encoding='utf-8')).get('items', []):
            old[it['path']] = it
    os.makedirs(FILES, exist_ok=True)
    items = []
    for rel, p in sorted(remote.items()):
        typ = p['type'] or mimetypes.guess_type(rel)[0] or ''
        item = {'name': os.path.basename(rel), 'path': rel, 'size': p['size'],
                'modified': iso(p['modified']), 'type': typ,
                'etag': p['etag']}
        local = os.path.join(FILES, rel)
        dav_file = dav_root + urllib.parse.quote(rel)
        if p['size'] > MAX_BYTES:
            d, f = os.path.split('/' + rel)
            item['url'] = (f'{base}/s/{token}/download?path='
                           f'{urllib.parse.quote(d)}&files='
                           f'{urllib.parse.quote(f)}')
            item['external'] = True
            if os.path.exists(local):
                os.remove(local)
        else:
            item['url'] = 'Final-Uploads/Files/' + urllib.parse.quote(rel)
            prev = old.get(rel)
            fresh = (prev and prev.get('etag') == p['etag']
                     and not prev.get('external') and os.path.exists(local)
                     and os.path.getsize(local) == p['size'])
            if not fresh:
                os.makedirs(os.path.dirname(local), exist_ok=True)
                tmp = local + '.part'
                with request('GET', dav_file, login) as r, \
                        open(tmp, 'wb') as fh:
                    shutil.copyfileobj(r, fh)
                os.replace(tmp, local)
                print('copied', rel)
        items.append(item)
    keep = {os.path.normpath(os.path.join(FILES, i['path']))
            for i in items if not i.get('external')}
    for d, _, names in os.walk(FILES, topdown=False):
        for n in names:
            f = os.path.normpath(os.path.join(d, n))
            if f not in keep:
                os.remove(f)
                print('removed', os.path.relpath(f, FILES))
        if d != FILES and not os.listdir(d):
            os.rmdir(d)
    items.sort(key=lambda i: (i['modified'], i['name']), reverse=True)
    before = None
    if os.path.exists(MANIFEST):
        before = json.load(open(MANIFEST, encoding='utf-8')).get('items')
    if before == items:
        print(f'no change: {len(items)} file(s)')
        return
    data = {'updated': datetime.now(timezone.utc).strftime(
        '%Y-%m-%dT%H:%M:%SZ'), 'items': items}
    with open(MANIFEST, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print(f'manifest updated: {len(items)} file(s)')


if __name__ == '__main__':
    main()
