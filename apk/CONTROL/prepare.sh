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


# Configuration
# =============
rsync -a --inplace --ignore-existing ${APKG_PKG_DIR}/conf.dist/ ${APKG_CFG_DIR}
chown -R ${APKG_USER}:${APKG_GROUP} ${APKG_CFG_DIR}
