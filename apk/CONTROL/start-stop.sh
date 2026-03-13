#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
. /usr/local/AppCentral/cappysan-apache/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1

LD_LIBRARY_PATH="${APKG_PKG_DIR}/lib:${LD_LIBRARY_PATH}"
mkdir -p  /var/log/apache /var/run/apache
chmod 750 /var/log/apache /var/run/apache

${APKG_PKG_DIR}/bin/install-hooks

function logger() {
  echo "${@}" >&2
  syslog --log 0 --level 0 --user SYSTEM --event "${@}"
}

# cf: apk/bin/install-hooks
export HOME=/share/Configuration/apache
case $1 in
  start)
    exit 0
    touch "${APKG_CFG_DIR}/active"
    ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k start
    logger "[Apache] Starting daemon..."
    ;;

  stop)
    if test -f "${APKG_CFG_DIR}/active"; then
      rm -f "${APKG_CFG_DIR}/active"
    fi
    ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k graceful-stop
    logger "[Apache] Stopping daemon..."
    ;;

  reload)
    if test -f "${APKG_CFG_DIR}/active"; then
      ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k graceful
      logger "[Apache] Reloading daemon..."
    fi
    ;;

  restart)
    ./CONTROL/start-stop.sh stop
    ./CONTROL/start-stop.sh start
    ;;

  *)
    echo "usage: $0 {start|stop|restart|reload}"
    exit 1
    ;;

esac
exit 0
