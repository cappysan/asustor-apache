#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
. /usr/local/AppCentral/cappysan-apache/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1
. ${APKG_PKG_DIR}/env

LD_LIBRARY_PATH="${APKG_PKG_DIR}/lib:${LD_LIBRARY_PATH}"
mkdir -p  /var/log/apache /var/run/apache
chmod 750 /var/log/apache /var/run/apache

case $1 in
  start)
    logger "[${WHAT}] Starting daemon..."
    touch "${APKG_PKG_DIR}/active"
    ./CONTROL/start-hook.sh
    ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k start
    ;;

  stop)
    logger "[${WHAT}] Stopping daemon..."
    rm -f "${APKG_PKG_DIR}/active"
    ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k graceful-stop
    ;;

  restart)
    ./CONTROL/start-stop.sh stop
    ./CONTROL/start-stop.sh start
    ;;

  reload)
    if test -f "${APKG_PKG_DIR}/active"; then
      logger "[${WHAT}] Graceful daemon restart..."
      ./CONTROL/start-hook.sh
      ${APKG_PKG_DIR}/apache/bin/apache2 -e warn -d "${APKG_PKG_DIR}/apache" -f "${APKG_PKG_DIR}"/apache/apache.conf -k graceful
    else
      logger "[${WHAT}] Service is stopped, cannot reload."
    fi
    ;;

  *)
    echo "usage: $0 {start|stop|restart|reload}"
    exit 1
    ;;
esac

exit 0
