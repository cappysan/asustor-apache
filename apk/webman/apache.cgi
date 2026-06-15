#!/bin/sh
# Apache UI CGI
# SPDX-License-Identifier: MIT

LOG=/tmp/apache-ui.log
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === invoked === method=$REQUEST_METHOD qs=$QUERY_STRING len=$CONTENT_LENGTH" >> "$LOG"

BODY=""
if [ "$REQUEST_METHOD" = "POST" ] && [ -n "$CONTENT_LENGTH" ] && [ "$CONTENT_LENGTH" -gt 0 ]; then
    BODY=$(dd bs=1 count="$CONTENT_LENGTH" 2>/dev/null)
fi

ALL_PARAMS="${QUERY_STRING}&${BODY}"

urldecode() {
    echo "$1" | awk 'BEGIN{
        for (i=0; i<256; i++) chr[sprintf("%02X", i)] = sprintf("%c", i)
    }
    {
        gsub(/\+/, " ")
        out = ""
        while (match($0, /%[0-9A-Fa-f][0-9A-Fa-f]/)) {
            out = out substr($0, 1, RSTART-1) chr[toupper(substr($0, RSTART+1, 2))]
            $0 = substr($0, RSTART+RLENGTH)
        }
        print out $0
    }'
}

get_param() {
    raw=$(echo "$ALL_PARAMS" | tr '&' '\n' | grep "^${1}=" | head -1 | cut -d= -f2-)
    urldecode "$raw"
}

ACT=$(get_param act)
TAB=$(get_param tab)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] act=$ACT tab=$TAB" >> "$LOG"

respond() {
    printf 'Content-Type: application/json\r\n\r\n'
    printf '%s' "$1"
}

CFG_DIR="/share/Configuration/apache"
if [ -n "$APKG_CFG_DIR" ]; then CFG_DIR="$APKG_CFG_DIR"; fi

find_python() {
    for P in python3 python /usr/local/bin/python3 /usr/bin/python3 /usr/bin/python; do
        if command -v "$P" >/dev/null 2>&1; then echo "$P"; return; fi
    done
}

case "$ACT" in

    get)
        PYTHON=$(find_python)
        if [ -z "$PYTHON" ]; then
            respond '{"success":false,"error_code":500,"error_msg":"No python interpreter found"}'
            exit 0
        fi

        case "$TAB" in
            settings)
                export _CFG_DIR="$CFG_DIR"
                RESULT=$("$PYTHON" - << '__PY__'
import json, os, re

cfg_dir = os.environ.get('_CFG_DIR', '/share/Configuration/apache')

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

print(json.dumps({
    'success':     True,
    'server_name': read_servername(os.path.join(cfg_dir, 'server-name.conf')),
    'domain':      read_define(os.path.join(cfg_dir, 'domain.conf'), 'domain'),
    'admin_email': read_define(os.path.join(cfg_dir, 'admin-email.conf'), 'admin_email'),
}))
__PY__
)
                printf 'Content-Type: application/json\r\n\r\n'
                printf '%s' "$RESULT"
                ;;

            sites)
                SITES_AVAILABLE="${CFG_DIR}/sites-available"
                SITES_ENABLED="${CFG_DIR}/sites-enabled"
                export _SITES_AVAILABLE="$SITES_AVAILABLE" _SITES_ENABLED="$SITES_ENABLED"
                RESULT=$("$PYTHON" - << '__PY__'
import json, os

available   = os.environ.get('_SITES_AVAILABLE', '')
enabled_dir = os.environ.get('_SITES_ENABLED', '')

sites = []
try:
    for name in sorted(os.listdir(available)):
        if not name.endswith('.conf'):
            continue
        enabled = os.path.exists(os.path.join(enabled_dir, name))
        sites.append({'name': name, 'enabled': enabled})
except Exception:
    pass

print(json.dumps({'success': True, 'sites': sites}))
__PY__
)
                printf 'Content-Type: application/json\r\n\r\n'
                printf '%s' "$RESULT"
                ;;

            hosts)
                HOSTS_FILE="${CFG_DIR}/deps.d/persistence/hosts"
                export _HOSTS_FILE="$HOSTS_FILE"
                RESULT=$("$PYTHON" - << '__PY__'
import json, os
path = os.environ.get('_HOSTS_FILE', '')
content = ''
try:
    with open(path) as f:
        content = f.read()
except Exception:
    pass
print(json.dumps({'success': True, 'content': content}))
__PY__
)
                printf 'Content-Type: application/json\r\n\r\n'
                printf '%s' "$RESULT"
                ;;

            *)
                respond '{"success":true}'
                ;;
        esac
        ;;

    get_content)
        SITE_NAME=$(get_param name)
        PYTHON=$(find_python)
        if [ -z "$PYTHON" ]; then
            respond '{"success":false,"error_code":500,"error_msg":"No python interpreter found"}'
            exit 0
        fi
        SITES_AVAILABLE="${CFG_DIR}/sites-available"
        export _SITE_PATH="${SITES_AVAILABLE}/${SITE_NAME}" _SITE_NAME="$SITE_NAME"
        RESULT=$("$PYTHON" - << '__PY__'
import json, os

path = os.environ.get('_SITE_PATH', '')
name = os.environ.get('_SITE_NAME', '')

if '/' in name or '..' in name or not name.endswith('.conf'):
    print(json.dumps({'success': False, 'content': ''}))
else:
    try:
        with open(path) as f:
            content = f.read()
    except Exception:
        content = ''
    print(json.dumps({'success': True, 'content': content}))
__PY__
)
        printf 'Content-Type: application/json\r\n\r\n'
        printf '%s' "$RESULT"
        ;;

    set)
        PYTHON=$(find_python)
        if [ -z "$PYTHON" ]; then
            respond '{"success":false,"error_code":500,"error_msg":"No python interpreter found"}'
            exit 0
        fi

        case "$TAB" in
            settings)
                SERVER_NAME=$(get_param server_name)
                DOMAIN=$(get_param domain)
                ADMIN_EMAIL=$(get_param admin_email)

                export _CFG_DIR="$CFG_DIR" _SERVER_NAME="$SERVER_NAME" \
                       _DOMAIN="$DOMAIN" _ADMIN_EMAIL="$ADMIN_EMAIL"

                "$PYTHON" - << '__PY__'
import os, re

cfg_dir     = os.environ.get('_CFG_DIR',     '/share/Configuration/apache')
server_name = os.environ.get('_SERVER_NAME', '').strip()
domain      = os.environ.get('_DOMAIN',      '').strip()
admin_email = os.environ.get('_ADMIN_EMAIL', '').strip()

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

if server_name:
    rewrite_servername(os.path.join(cfg_dir, 'server-name.conf'), server_name)
if domain:
    rewrite_define(os.path.join(cfg_dir, 'domain.conf'), 'domain', domain)
if admin_email:
    rewrite_define(os.path.join(cfg_dir, 'admin-email.conf'), 'admin_email', admin_email)
__PY__

                /usr/local/AppCentral/cappysan-apache/CONTROL/start-stop.sh reload >> "$LOG" 2>&1
                respond '{"success":true}'
                ;;

            sites)
                SITE_NAME=$(get_param name)
                SITE_ENABLED=$(get_param enabled)
                SITES_AVAILABLE="${CFG_DIR}/sites-available"
                SITES_ENABLED="${CFG_DIR}/sites-enabled"

                case "$SITE_NAME" in
                    */*|*..*)
                        respond '{"success":false,"error_msg":"Invalid site name"}'
                        exit 0 ;;
                    *.conf) ;;
                    *)
                        respond '{"success":false,"error_msg":"Invalid site name"}'
                        exit 0 ;;
                esac

                if [ "$SITE_NAME" = "_default_.conf" ] && [ "$SITE_ENABLED" != "true" ]; then
                    respond '{"success":false,"error_msg":"_default_.conf cannot be disabled"}'
                    exit 0
                fi

                CONF_AVAILABLE="${SITES_AVAILABLE}/${SITE_NAME}"
                CONF_ENABLED="${SITES_ENABLED}/${SITE_NAME}"

                if [ ! -f "$CONF_AVAILABLE" ]; then
                    respond '{"success":false,"error_msg":"Site configuration not found"}'
                    exit 0
                fi

                mkdir -p "$SITES_ENABLED"

                if [ "$SITE_ENABLED" = "true" ]; then
                    rm -f "$CONF_ENABLED" 2>/dev/null
                    ln -s "../sites-available/${SITE_NAME}" "$CONF_ENABLED"
                else
                    rm -f "$CONF_ENABLED" 2>/dev/null
                fi

                /usr/local/AppCentral/cappysan-apache/CONTROL/start-stop.sh reload >> "$LOG" 2>&1
                respond '{"success":true}'
                ;;

            hosts)
                HOSTS_CONTENT=$(get_param content)
                HOSTS_FILE="${CFG_DIR}/deps.d/persistence/hosts"
                mkdir -p "$(dirname "$HOSTS_FILE")"
                printf '%s' "$HOSTS_CONTENT" > "$HOSTS_FILE"
                if [ -s "$HOSTS_FILE" ] && [ "$(tail -c 1 "$HOSTS_FILE" | wc -l)" -eq 0 ]; then
                    printf '\n' >> "$HOSTS_FILE"
                fi
                chmod 640 "$HOSTS_FILE" 2>/dev/null

                PERSIST_SCRIPT="/usr/local/AppCentral/cappysan-persistence/CONTROL/start-stop.sh"
                if [ ! -f "$PERSIST_SCRIPT" ]; then
                    respond '{"success":true,"warning":"cappysan-persistence package is not installed."}'
                elif ! "$PERSIST_SCRIPT" restart >> "$LOG" 2>&1; then
                    respond '{"success":true,"warning":"Failed to restart cappysan-persistence."}'
                else
                    respond '{"success":true}'
                fi
                ;;

            *)
                respond '{"success":true}'
                ;;
        esac
        ;;

    *)
        respond '{"success":false,"error_code":400,"error_msg":"Unknown action"}'
        ;;
esac
exit 0
