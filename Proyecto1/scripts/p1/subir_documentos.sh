#!/bin/bash
# Genera los PDF del gestor y los sube a Odoo
# ./subir_documentos.sh pdf    -> crea los PDF en documentos/pdf
# ./subir_documentos.sh subir  -> los sube al gestor con carpeta, categoria y etiquetas
set -euo pipefail
cd "$(dirname "$0")"
set -a; . ./.env; set +a
KEY="$HOME/.ssh/qm_gcp"
SSH() { ssh -i "$KEY" "qmadmin@$STATIC_IP" "$@"; }
SCP() { scp -q -i "$KEY" "$@"; }
DOCS=../../documentos

case "${1:-}" in
  pdf)
    python generar_documentos.py
    SSH 'rm -rf ~/quetzalmart/docs && mkdir -p ~/quetzalmart/docs/pdf && chmod 777 ~/quetzalmart/docs/pdf'
    SCP -r "$DOCS/html" "$DOCS/manifiesto.json" "qmadmin@$STATIC_IP:~/quetzalmart/docs/"
    # se usa el wkhtmltopdf que trae la imagen de odoo
    SSH 'cd ~/quetzalmart && docker compose run --rm -T --entrypoint sh -v $PWD/docs:/docs odoo -c \
      "for f in /docs/html/*.html; do wkhtmltopdf -q --encoding utf-8 -s Letter \"\$f\" /docs/pdf/\$(basename \"\${f%.html}\").pdf; done"'
    mkdir -p "$DOCS/pdf"
    SCP "qmadmin@$STATIC_IP:~/quetzalmart/docs/pdf/*.pdf" "$DOCS/pdf/"
    ls -1 "$DOCS/pdf"
    ;;
  subir)
    SCP cargar_documentos.py "qmadmin@$STATIC_IP:~/quetzalmart/"
    SSH 'cd ~/quetzalmart && docker compose run --rm -T -v $PWD/docs:/tmp/docs:ro \
      -v $PWD/cargar_documentos.py:/tmp/s.py:ro odoo sh -c \
      "odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http < /tmp/s.py" 2>&1 | grep -E "^OK|Error|Traceback|line [0-9]+"'
    ;;
  *)
    echo "Uso: $0 pdf | subir" >&2; exit 1 ;;
esac
