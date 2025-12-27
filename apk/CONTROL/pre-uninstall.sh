#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
. /usr/local/AppCentral/cappysan-apache/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1

if test -f /etc/logrotate.d/cappysan-apache; then
  logrotate -f /etc/logrotate.d/cappysan-apache
  rm -f /etc/logrotate.d/cappysan-apache
fi

exit 0
