#!/bin/bash
# Respaldo de la base (Cloud SQL) y snapshot del disco de la VM
# Uso: ./respaldo_manual.sh "descripcion"
set -euo pipefail
cd "$(dirname "$0")"
set -a; . ./.env; set +a
ETIQUETA="${1:-respaldo manual}"
SELLO=$(date +%Y%m%d-%H%M)

gcloud sql backups create --instance="$SQL_INSTANCE" --project="$PROJECT_ID" \
  --description="$ETIQUETA $SELLO"
gcloud compute snapshots create "qm-odoo-$SELLO" --project="$PROJECT_ID" \
  --source-disk=qm-odoo --source-disk-zone="$ZONE" --description="$ETIQUETA"

gcloud sql backups list --instance="$SQL_INSTANCE" --project="$PROJECT_ID" --limit=3
gcloud compute snapshots list --project="$PROJECT_ID" --limit=3
