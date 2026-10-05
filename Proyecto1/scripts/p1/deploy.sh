#!/bin/bash
# Sube la configuracion a la VM y levanta los contenedores
# Uso: ./deploy.sh
set -euo pipefail
cd "$(dirname "$0")"
set -a; . ./.env; set +a

SSH_KEY="$HOME/.ssh/qm_gcp"
VM="qmadmin@$STATIC_IP"
SQL_IP=$(gcloud sql instances describe "$SQL_INSTANCE" --project="$PROJECT_ID" \
  --format='value(ipAddresses[0].ipAddress)')
export SQL_IP

# genera odoo.conf a partir de la plantilla
perl -pe 's/\$\{(\w+)\}/$ENV{$1}/g' odoo.conf.template > odoo.conf

ssh -i "$SSH_KEY" "$VM" 'mkdir -p ~/quetzalmart/addons'
scp -i "$SSH_KEY" docker-compose.yml Caddyfile odoo.conf "$VM:~/quetzalmart/"

# clona el modulo dms si no existe y levanta odoo
ssh -i "$SSH_KEY" "$VM" '
  cd ~/quetzalmart
  if [ ! -d oca/dms ]; then git clone --depth 1 -b 18.0 https://github.com/OCA/dms.git oca/dms; fi
  docker compose pull -q
  docker compose up -d
  docker compose ps'
