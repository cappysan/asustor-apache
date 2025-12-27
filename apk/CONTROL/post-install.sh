#!/usr/bin/env sh
# SPDX-License-Identifier: MIT
#
# ------------------------------------------------------------------------------
# Save variables
APKG_PKG_DIR=/usr/local/AppCentral/${APKG_PKG_NAME}
APKG_PKG_SHORT_VER="${APKG_PKG_VER%-*}"
APKG_CFG_DIR=/share/Configuration/apache
export APKG_CFG_DIR APKG_PKG_VER APKG_PKG_SHORT_VER
env | grep APKG | grep -v " " | sort > ${APKG_PKG_DIR}/.env.install

${APKG_PKG_DIR}/CONTROL/common.sh

exit 0
