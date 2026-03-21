#!/usr/bin/env sh
#
#
. /usr/local/AppCentral/cappysan-apache/.env.install
cd ${APKG_PKG_DIR:-/nonexistent} || exit 1

mkdir -p ${APKG_CFG_DIR}/sites-available/
mkdir -p ${APKG_CFG_DIR}/sites-enabled/
mkdir -p ${APKG_CFG_DIR}/logs/

for as_dir in /usr/local/AppCentral/cappysan-*/sites-available.dist; do
  if test -d "${as_dir}"; then
    rsync -a --inplace --ignore-existing ${as_dir}/ \
      ${APKG_CFG_DIR}/sites-available/
  fi
done

# Enable logrotate
cp -f ${APKG_CFG_DIR}/logrotate.d/cappysan-apache /etc/logrotate.d/

# If there's a hosts.d folder, persistence will copy them over to /etc/hosts
if test -f /usr/local/AppCentral/cappysan-persistence/CONTROL/install-hooks.d/hosts.sh; then
  /usr/local/AppCentral/cappysan-persistence/CONTROL/install-hooks.d/hosts.sh
fi

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
