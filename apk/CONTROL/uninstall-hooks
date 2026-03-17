#!/usr/bin/env sh
#
#
. /usr/local/AppCentral/cappysan-certbot/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1

function logger() {
  echo "${@}" >&2
  syslog --log 0 --level 0 --user SYSTEM --event "${@}"
}
