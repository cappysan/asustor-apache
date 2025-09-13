#!/usr/bin/env sh
#
as_apk=/usr/local/AppCentral/cappysan-apache

LD_LIBRARY_PATH="${as_apk}/lib:${LD_LIBRARY_PATH}"

if test ! -d /var/log/apache; then
  mkdir /var/log/apache
fi
chmod 750 /var/log/apache

case $1 in
  start)
    ${as_apk}/bin/apache2 -e warn -d "${as_apk}" -f "${as_apk}"/apache.conf -k start
    ;;

  stop)
    ${as_apk}/bin/apache2 -e warn -d "${as_apk}" -f "${as_apk}"/apache.conf -k graceful-stop
    ;;

  reload)
    ${as_apk}/bin/apache2 -e warn -d "${as_apk}" -f "${as_apk}"/apache.conf -k graceful
    ;;

  restart)
    $0 stop
    $0 start
    ;;

  *)
    echo "usage: $0 {start|stop|restart|reload}"
    exit 1
    ;;

esac
exit 0
