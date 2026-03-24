#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
# ------------------------------------------------------------------------------
# Save variables
APKG_PKG_DIR=/usr/local/AppCentral/${APKG_PKG_NAME}
APKG_PKG_SHORT_VER="${APKG_PKG_VER%-*}"
APKG_CFG_DIR=/share/Configuration/apache
export APKG_CFG_DIR APKG_PKG_VER APKG_PKG_SHORT_VER
env | grep APKG | grep -v APKG_PKG_STATUS \
  | grep -v " " | sort > ${APKG_PKG_DIR}/.env.install

cd ${APKG_PKG_DIR:-/nonexistent} || exit 1
. ${APKG_PKG_DIR}/env

# Permissions
# ===========
# Ensure permissions are limited to root user for the application folder.
chown -R root:root ${APKG_PKG_DIR}


# User
# ====
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
# Don't override files that could have been user modified.
rsync -a --inplace --ignore-existing ${APKG_PKG_DIR}/conf.dist/ ${APKG_CFG_DIR}
chown -R ${APKG_USER}:${APKG_GROUP} ${APKG_CFG_DIR}/*

exit 0
