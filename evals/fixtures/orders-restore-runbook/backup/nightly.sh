#!/bin/sh
# Nightly custom-format dump of the orders database to S3.
set -eu

HERE=$(dirname "$0")
STAMP=$(date -u +%Y%m%d)
DUMP=/srv/backup/orders-$STAMP.dump

SKIP_DATA=""
while read -r table _; do
  case "$table" in ''|'#'*) continue ;; esac
  SKIP_DATA="$SKIP_DATA --exclude-table-data=$table"
done < "$HERE/exclude.conf"

# shellcheck disable=SC2086
pg_dump -Fc $SKIP_DATA -d orders -f "$DUMP"
aws s3 cp "$DUMP" s3://acme-backups/orders/
rm -f "$DUMP"
