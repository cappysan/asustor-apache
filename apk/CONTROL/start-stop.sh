#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
. /usr/local/AppCentral/cappysan-apache/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1

LD_LIBRARY_PATH="${APKG_PKG_DIR}/lib:${LD_LIBRARY_PATH}"
mkdir -p  /var/log/apache /var/run/apache
chmod 750 /var/log/apache /var/run/apache


function logger() {
  echo "${@}" >&2
  syslog --log 0 --level 0 --user SYSTEM --event "${@}"
}

# cf: apk/CONTROL/install-hooks.sh
export HOME=/share/Configuration/apache
case $1 in
  start)
    logger "[Apache] Starting daemon..."
    touch "${APKG_CFG_DIR}/active"
    ${APKG_PKG_DIR}/CONTROL/install-hooks.sh
    ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k start
    ;;

  stop)
    logger "[Apache] Stopping daemon..."
    rm -f "${APKG_CFG_DIR}/active"
    ${APKG_PKG_DIR}/CONTROL/uninstall-hooks.sh
    ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k graceful-stop
    ;;

  reload)
    logger "[Apache] Reloading..."
    if test -f "${APKG_CFG_DIR}/active"; then
      ${APKG_PKG_DIR}/CONTROL/install-hooks.sh
      ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k graceful
    fi
    ;;

  restart)
    logger "[Apache] Restarting daemon..."
    if test -f "${APKG_CFG_DIR}/active"; then
      ./CONTROL/start-stop.sh stop
      ./CONTROL/start-stop.sh start
    fi
    ;;

  *)
    echo "usage: $0 {start|stop|restart|reload}"
    exit 1
    ;;

esac
exit 0
