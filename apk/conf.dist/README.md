# Files

## admin-email.conf

Set the admin email.


## domain.conf

Set the base domain of the server (eg: example.com), supports subdomains such as int.example.com

Do not use a wildcard such as `*`


## server-name

This is the FQDN of the server, so if the server is on example.com domain, the ServerName could be nas.example.com if the NAS hostname is `nas`


# Sites Enabled

The recommended method is to symlink a file from sites-available to sites-enabled.

Otherwise, to enable a site, either copy the file from sites-available to sites-enabled.# deps.d


# deps.d

Files in `/usr/local/AppCentral/cappysan-*/deps.d/apache/` will always overwrite files that have been moved to `/share/Configuration/apache/sites-available`.

Files in `/share/Configuration/*/deps.d/*/` will never overwrite files that have been moved to `/share/Configuration/apache/sites-available`.
