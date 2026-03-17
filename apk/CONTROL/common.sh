#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
. /usr/local/AppCentral/cappysan-apache/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1

# Ensure permissions are limited to root user for the application folder.
chown -R root:root ${APKG_PKG_DIR}


# User
# ====
APKG_USER=as-www-data
APKG_GROUP=root
useradd --system --no-create-home --home-dir ${APKG_CFG_DIR}/ --gid nogroup --shell /bin/false ${APKG_USER}


# Configuration folder
# ====================
# Don't overwrite user permissions if set manually
if test ! -d ${APKG_CFG_DIR}; then
  mkdir -p ${APKG_CFG_DIR}
  chown -R ${APKG_USER}:${APKG_GROUP} ${APKG_CFG_DIR}
  chmod 750 ${APKG_CFG_DIR}
fi


# Backups
# =======
mkdir ${APKG_CFG_DIR}/backups/
as_date="$(date +%Y-%m-%d_%H%M)"
if test ! -f ${APKG_CFG_DIR}/installed.json.${as_date}.bak; then
  cp /usr/builtin/etc/appcentral/installed.json ${APKG_CFG_DIR}/backups/installed.json.${as_date}.bak
fi
if test ! -f ${APKG_CFG_DIR}/crontab.${as_date}.bak; then
  crontab -l > ${APKG_CFG_DIR}/backups/crontab.${as_date}.bak
fi
chown -R ${APKG_USER}:${APKG_GROUP} ${APKG_CFG_DIR}/backups


# Configuration
# =============
rsync -a --inplace --ignore-existing ${APKG_PKG_DIR}/conf.dist/ ${APKG_CFG_DIR}
chown -R ${APKG_USER}:${APKG_GROUP} ${APKG_CFG_DIR}
