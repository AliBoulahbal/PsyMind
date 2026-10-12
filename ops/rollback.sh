#!/bin/sh
set -eu
echo "Application rollback requires the previous immutable image/tag."
echo "Do NOT automatically downgrade database migrations after clinical writes."
echo "Restore DB only from a verified backup under an explicit incident procedure."
