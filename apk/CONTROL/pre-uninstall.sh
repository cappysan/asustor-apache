#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
. /usr/local/AppCentral/cappysan-apache/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1
if test -f ${APKG_PKG_DIR}/env; then
  . ${APKG_PKG_DIR}/env
fi

# Clean
# =====
if test "x${APKG_PKG_STATUS}" != "xupgrade"; then
  # Remove logrotate
  rm -f /etc/logrotate.d/cappysan-apache
fi

# ------------------------------------------------------------------------------
exit 0
