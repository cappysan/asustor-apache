#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
# ------------------------------------------------------------------------------
. /usr/local/AppCentral/cappysan-apache/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1
. ${APKG_PKG_DIR}/env


# Folders
# =======
mkdir -p ${APKG_CFG_DIR}/sites-available/
mkdir -p ${APKG_CFG_DIR}/sites-enabled/
mkdir -p ${APKG_CFG_DIR}/logs/
mkdir -p  /var/log/apache /var/run/apache
chmod 750 /var/log/apache /var/run/apache


# Logrotate
# =========
# Enable logrotate
cp -f ${APKG_CFG_DIR}/deps.d/logrotate.d/* /etc/logrotate.d/


# Sites Available
# ===============
# Ensure with a first pass that default site configs are always present
rsync -a --inplace --ignore-existing ${APKG_PKG_DIR}/conf.dist/sites-available/ ${APKG_CFG_DIR}/sites-available/

for as_dir in /usr/local/AppCentral/cappysan-*/deps.d/apache/sites-available/; do
  if test -d "${as_dir}"; then
    rsync -a --inplace ${as_dir}/ ${APKG_CFG_DIR}/sites-available/
  fi
done
for as_dir in /share/Configuration/*/deps.d/apache/sites-available/; do
  if test -d "${as_dir}"; then
    rsync -a --inplace --ignore-existing ${as_dir}/ ${APKG_CFG_DIR}/sites-available/
  fi
done


# Symlinks
# ========
# If two files are the same, then symlink them
for as_file in ${APKG_CFG_DIR}/sites-enabled/*.conf; do
  if test ! -L ${as_file}; then
    as_file=$(basename ${as_file})

    for as_src in ${APKG_CFG_DIR}/sites-available/*.conf; do
      as_src=$(basename ${as_src})
      if diff -bq ${APKG_CFG_DIR}/sites-available/${as_src} ${APKG_CFG_DIR}/sites-enabled/${as_file} >/dev/null 2>&1; then
        ln -sf -T ../sites-available/${as_src} ${APKG_CFG_DIR}/sites-enabled/${as_file}
      fi
    done
  fi
done


# Dependencies
# ============
export DOCKER_RELOAD=${DOCKER_RELOAD:-0}
export CERTBOT_RELOAD=${CERTBOT_RELOAD:-0}
/usr/local/AppCentral/cappysan-persistence/CONTROL/start-stop.sh reload
/usr/local/AppCentral/cappysan-certbot/CONTROL/start-stop.sh reload

exit 0
