#!/usr/bin/env bash

set -euo pipefail

# =========================
# Configuración (editar)
# =========================
DB_HOST="127.0.0.1"
DB_PORT="5432"
DB_NAME="prod_kosmo"
DB_USER="postgres"

# Carpeta donde se guardarán los respaldos
BACKUP_DIR="/var/backups/kosmo"

# Días de retención (borra respaldos más antiguos)
DAILY_RETENTION_DAYS=14
WEEKLY_RETENTION_DAYS=60

# Día de respaldo semanal (1=lunes ... 7=domingo)
WEEKLY_BACKUP_DAY=7

# Si prefieres no usar .pgpass, exporta PGPASSWORD antes de ejecutar:
# export PGPASSWORD='tu_password'

TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
DAY_OF_WEEK="$(date +"%u")"

DAILY_DIR="${BACKUP_DIR}/daily"
WEEKLY_DIR="${BACKUP_DIR}/weekly"

create_backup() {
  local target_dir="$1"
  local prefix="$2"
  local retention_days="$3"
  local filename="${prefix}_${DB_NAME}_${TIMESTAMP}.sql.gz"
  local tmp_file="${target_dir}/${prefix}_${DB_NAME}_${TIMESTAMP}.sql"
  local final_file="${target_dir}/${filename}"

  mkdir -p "${target_dir}"

  echo "[$(date +"%F %T")] Iniciando backup ${prefix} de ${DB_NAME}..."

  pg_dump \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --username="${DB_USER}" \
    --format=plain \
    --no-owner \
    --no-privileges \
    "${DB_NAME}" > "${tmp_file}"

  gzip -f "${tmp_file}"

  echo "[$(date +"%F %T")] Backup ${prefix} generado: ${final_file}"

  find "${target_dir}" -type f -name "${prefix}_${DB_NAME}_*.sql.gz" -mtime +"${retention_days}" -delete

  echo "[$(date +"%F %T")] Limpieza ${prefix} completada (retención: ${retention_days} días)."
}

create_backup "${DAILY_DIR}" "daily" "${DAILY_RETENTION_DAYS}"

if [[ "${DAY_OF_WEEK}" == "${WEEKLY_BACKUP_DAY}" ]]; then
  create_backup "${WEEKLY_DIR}" "weekly" "${WEEKLY_RETENTION_DAYS}"
else
  echo "[$(date +"%F %T")] Hoy no corresponde respaldo semanal (día actual: ${DAY_OF_WEEK})."
fi
