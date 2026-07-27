#!/usr/local/bin/python3
# Apache UI CGI
# SPDX-License-Identifier: MIT

import json
import os
import re
import subprocess
import sys
from urllib.parse import parse_qs

REQUEST_METHOD = os.environ.get('REQUEST_METHOD', '')
QUERY_STRING   = os.environ.get('QUERY_STRING', '')
CONTENT_LENGTH = os.environ.get('CONTENT_LENGTH', '')
APKG_CFG_DIR   = os.environ.get('APKG_CFG_DIR', '')

CFG_DIR             = APKG_CFG_DIR or '/share/Configuration/apache'
SITES_AVAILABLE     = os.path.join(CFG_DIR, 'sites-available')
SITES_ENABLED       = os.path.join(CFG_DIR, 'sites-enabled')
DEFAULT_CONF_TARGET = os.path.join(SITES_AVAILABLE, '_default_.conf')
HOSTS_FILE          = os.path.join(CFG_DIR, 'deps.d', 'persistence', 'hosts')

APACHE_CONTROL      = '/usr/local/AppCentral/cappysan-apache/CONTROL/start-stop.sh'
PERSISTENCE_CONTROL = '/usr/local/AppCentral/cappysan-persistence/CONTROL/start-stop.sh'
PERSISTENCE_CONFIG  = '/usr/local/AppCentral/cappysan-persistence/CONTROL/config.json'


def get_params():
    body = ''
    if REQUEST_METHOD == 'POST' and CONTENT_LENGTH:
        try:
            length = int(CONTENT_LENGTH)
        except ValueError:
            length = 0
        if length > 0:
            body = sys.stdin.read(length)

    params = {}
    for source in (QUERY_STRING, body):
        if not source:
            continue
        for key, values in parse_qs(source, keep_blank_values=True).items():
            if values:
                params[key] = values[0]
    return params


def param(params, key, default=''):
    return params.get(key, default)


def respond(data):
    print('Content-Type: application/json\r\n\r\n' + json.dumps(data), end='', flush=True)


def read_file(path, default=''):
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return default


def read_define(path, key):
    try:
        with open(path) as f:
            for line in f:
                s = line.strip()
                if s.startswith('#'):
                    continue
                m = re.match(r'^Define\s+' + re.escape(key) + r'\s+(.+)$', s)
                if m:
                    return m.group(1).strip()
    except Exception:
        pass
    return ''


def read_servername(path):
    try:
        with open(path) as f:
            for line in f:
                s = line.strip()
                if s.startswith('#'):
                    continue
                m = re.match(r'^ServerName\s+(.+)$', s)
                if m:
                    return m.group(1).strip()
    except Exception:
        pass
    return ''


def read_custom_env(path, key):
    try:
        with open(path) as f:
            for line in f:
                s = line.strip()
                if s.startswith('#') or '=' not in s:
                    continue
                k, v = s.split('=', 1)
                if k.strip() == key:
                    return v.strip()
    except Exception:
        pass
    return ''


def rewrite_define(path, key, value):
    try:
        with open(path) as f:
            lines = f.readlines()
    except Exception:
        lines = []
    pattern = re.compile(r'^#?\s*Define\s+' + re.escape(key) + r'\s+', re.IGNORECASE)
    found = False
    out = []
    for line in lines:
        if pattern.match(line):
            out.append('Define %s %s\n' % (key, value))
            found = True
        else:
            out.append(line)
    if not found and value:
        out.append('Define %s %s\n' % (key, value))
    with open(path, 'w') as f:
        f.writelines(out)


def rewrite_servername(path, value):
    try:
        with open(path) as f:
            lines = f.readlines()
    except Exception:
        lines = []
    pattern = re.compile(r'^#?\s*ServerName\s+', re.IGNORECASE)
    found = False
    out = []
    for line in lines:
        if pattern.match(line):
            out.append(('ServerName %s\n' % value) if value else '# ServerName nas.example.com\n')
            found = True
        else:
            out.append(line)
    if not found and value:
        out.append('ServerName %s\n' % value)
    with open(path, 'w') as f:
        f.writelines(out)


def rewrite_custom_env(path, key, value):
    try:
        with open(path) as f:
            lines = f.readlines()
    except Exception:
        lines = []
    found = False
    out = []
    for line in lines:
        s = line.strip()
        if not s.startswith('#') and '=' in s and s.split('=', 1)[0].strip() == key:
            out.append('%s=%s\n' % (key, value))
            found = True
        else:
            out.append(line)
    if not found:
        out.append('%s=%s\n' % (key, value))
    with open(path, 'w') as f:
        f.writelines(out)


def run_control(path, arg):
    if not os.path.isfile(path):
        return None
    try:
        proc = subprocess.run([path, arg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc.returncode == 0
    except Exception:
        return False


def get_settings():
    return {
        'success':          True,
        'server_name':      read_servername(os.path.join(CFG_DIR, 'server-name.conf')),
        'domain':           read_define(os.path.join(CFG_DIR, 'domain.conf'), 'domain'),
        'admin_email':      read_define(os.path.join(CFG_DIR, 'admin-email.conf'), 'admin_email'),
        'web_url_override': read_custom_env(os.path.join(CFG_DIR, 'custom.env'), 'WEB_URL_OVERRIDE'),
    }


def get_sites():
    sites = []
    try:
        for name in sorted(os.listdir(SITES_AVAILABLE)):
            if not name.endswith('.conf'):
                continue
            sites.append({'name': name, 'enabled': os.path.exists(os.path.join(SITES_ENABLED, name))})
    except Exception:
        pass
    return {'success': True, 'sites': sites}


def get_hosts():
    return {'success': True, 'content': read_file(HOSTS_FILE)}


def get_apache():
    hostname = 'nas'
    fqdn     = '${hostname}.${domain}'
    redirect = 'https://${server_fqdn}/'
    proxy_to = 'https://127.0.0.1:8001/'

    if os.path.isfile(DEFAULT_CONF_TARGET):
        hostname = read_define(DEFAULT_CONF_TARGET, 'hostname') or hostname
        fqdn     = read_define(DEFAULT_CONF_TARGET, 'server_fqdn') or fqdn
        redirect = read_define(DEFAULT_CONF_TARGET, 'redirect_to') or redirect
        proxy_to = read_define(DEFAULT_CONF_TARGET, 'proxy_to') or proxy_to

    return {
        'success':            True,
        'apache_hostname':    hostname,
        'apache_fqdn':        fqdn,
        'apache_redirect_to': redirect,
        'apache_proxy_to':    proxy_to,
    }


def get_content(params):
    name = param(params, 'name')
    if '/' in name or '..' in name or not name.endswith('.conf'):
        return {'success': False, 'content': ''}
    return {'success': True, 'content': read_file(os.path.join(SITES_AVAILABLE, name))}


def set_settings(params):
    server_name  = param(params, 'server_name').strip()
    domain       = param(params, 'domain').strip()
    admin_email  = param(params, 'admin_email').strip()
    url_override = param(params, 'web_url_override').strip()

    if server_name:
        rewrite_servername(os.path.join(CFG_DIR, 'server-name.conf'), server_name)
    if domain:
        rewrite_define(os.path.join(CFG_DIR, 'domain.conf'), 'domain', domain)
    if admin_email:
        rewrite_define(os.path.join(CFG_DIR, 'admin-email.conf'), 'admin_email', admin_email)
    rewrite_custom_env(os.path.join(CFG_DIR, 'custom.env'), 'WEB_URL_OVERRIDE', url_override)

    return {'success': True}


def set_sites(params):
    name    = param(params, 'name')
    enabled = param(params, 'enabled')

    if '/' in name or '..' in name or not name.endswith('.conf'):
        return {'success': False, 'error_msg': 'Invalid site name'}

    if name == '_default_.conf' and enabled != 'true':
        return {'success': False, 'error_msg': '_default_.conf cannot be disabled'}

    conf_available = os.path.join(SITES_AVAILABLE, name)
    conf_enabled   = os.path.join(SITES_ENABLED, name)

    if not os.path.isfile(conf_available):
        return {'success': False, 'error_msg': 'Site configuration not found'}

    os.makedirs(SITES_ENABLED, exist_ok=True)

    try:
        os.remove(conf_enabled)
    except Exception:
        pass

    if enabled == 'true':
        os.symlink(os.path.join('..', 'sites-available', name), conf_enabled)

    run_control(APACHE_CONTROL, 'reload')
    return {'success': True}


def set_hosts(params):
    content = param(params, 'content')
    os.makedirs(os.path.dirname(HOSTS_FILE), exist_ok=True)
    with open(HOSTS_FILE, 'w') as f:
        f.write(content)
        if content and not content.endswith('\n'):
            f.write('\n')
    try:
        os.chmod(HOSTS_FILE, 0o640)
    except Exception:
        pass

    if not os.path.isfile(PERSISTENCE_CONTROL):
        return {'success': True, 'warning': 'cappysan-persistence package is not installed.'}
    if not run_control(PERSISTENCE_CONTROL, 'restart'):
        return {'success': True, 'warning': 'Failed to restart cappysan-persistence.'}
    return {'success': True}


def set_apache(params):
    hostname = param(params, 'apache_hostname') or 'nas'
    fqdn     = param(params, 'apache_fqdn') or '${hostname}.${domain}'
    redirect = param(params, 'apache_redirect_to') or 'https://${server_fqdn}/'
    proxy_to = param(params, 'apache_proxy_to') or 'https://127.0.0.1:8001/'

    os.makedirs(SITES_AVAILABLE, exist_ok=True)

    try:
        with open(DEFAULT_CONF_TARGET) as f:
            lines = f.readlines()
    except Exception:
        lines = []

    keys_found = {'hostname': False, 'server_fqdn': False, 'redirect_to': False, 'proxy_to': False}

    out = []
    for line in lines:
        if line.startswith('Define hostname '):
            out.append('Define hostname    %s\n' % hostname)
            keys_found['hostname'] = True
        elif line.startswith('Define server_fqdn '):
            out.append('Define server_fqdn %s\n' % fqdn)
            keys_found['server_fqdn'] = True
        elif line.startswith('Define redirect_to '):
            out.append('Define redirect_to %s\n' % redirect)
            keys_found['redirect_to'] = True
        elif line.startswith('Define proxy_to '):
            out.append('Define proxy_to    %s\n' % proxy_to)
            keys_found['proxy_to'] = True
        else:
            out.append(line)

    # If the file was missing, empty, or simply never had these Define lines
    # (e.g. fresh install before conf.dist seeding ran), write them fresh so
    # the save is never silently a no-op.
    prelude = []
    if not keys_found['hostname']:
        prelude.append('Define hostname    %s\n' % hostname)
    if not keys_found['server_fqdn']:
        prelude.append('Define server_fqdn %s\n' % fqdn)
    if not keys_found['redirect_to']:
        prelude.append('Define redirect_to %s\n' % redirect)
    if not keys_found['proxy_to']:
        prelude.append('Define proxy_to    %s\n' % proxy_to)

    if prelude:
        out = prelude + (['\n'] if out else []) + out

    with open(DEFAULT_CONF_TARGET, 'w') as f:
        f.writelines(out)

    return {'success': True}


def check_persistence():
    return {'success': True, 'installed': os.path.isfile(PERSISTENCE_CONFIG)}


def reload_apache():
    if not os.path.isfile(APACHE_CONTROL):
        return {'success': True, 'warning': 'cappysan-apache package is not installed.'}
    if not run_control(APACHE_CONTROL, 'reload'):
        return {'success': True, 'warning': 'Failed to reload cappysan-apache.'}
    return {'success': True}


def restart_apache():
    if not os.path.isfile(APACHE_CONTROL):
        return {'success': True, 'warning': 'cappysan-apache package is not installed.'}
    if not run_control(APACHE_CONTROL, 'restart'):
        return {'success': True, 'warning': 'Failed to restart cappysan-apache.'}
    return {'success': True}


PARAMS = get_params()
ACT    = param(PARAMS, 'act')
TAB    = param(PARAMS, 'tab')

if ACT == 'get':
    if TAB == 'settings':
        respond(get_settings())
    elif TAB == 'sites':
        respond(get_sites())
    elif TAB == 'hosts':
        respond(get_hosts())
    elif TAB == 'apache':
        respond(get_apache())
    else:
        respond({'success': True})

elif ACT == 'get_content':
    respond(get_content(PARAMS))

elif ACT == 'set':
    if TAB == 'settings':
        respond(set_settings(PARAMS))
    elif TAB == 'sites':
        respond(set_sites(PARAMS))
    elif TAB == 'hosts':
        respond(set_hosts(PARAMS))
    elif TAB == 'apache':
        respond(set_apache(PARAMS))
    else:
        respond({'success': True})

elif ACT == 'check_persistence':
    respond(check_persistence())

elif ACT == 'reload':
    respond(reload_apache())

elif ACT == 'restart':
    respond(restart_apache())

else:
    respond({'success': False, 'error_code': 400, 'error_msg': 'Unknown action'})
