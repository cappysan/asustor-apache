#!/usr/bin/env sh
#
# Ensure permissions limit to root user.
chown -R 0:0 ${APKG_PKG_DIR}

mkdir -p /share/Configuration/apache/htdocs/

rsync -av --inplace --ignore-existing /usr/local/AppCentral/cappysan-apache/conf.dist/ /share/Configuration/apache/

for as_dir in jellyfin; do
  mkdir -p /share/Configuration/apache/log/${as_dir}/
done

# /usr/local/AppCentral/httpd-2.4.43/data/conf/asustor.conf
# [Web Center]
# EnableHttp=No
# EnableHttps=No
exit 0
