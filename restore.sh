#!/usr/bin/env bash
set -euo pipefail

# === Configura aquí si hace falta ===
BACKUP_DIR="/home/ubuntu/proyectos/AFD"
FILE_SENSOR="backup_sensorDB_2025-07-29_17-20-51.sql"
FILE_DEFAULT="backup_default_2025-07-29_17-20-51.sql"

# Usaremos nombres en minúsculas para evitar problemas de quoting
DB_SENSOR="sensordb"
DB_DEFAULT="afd"
OWNER_ROLE="postgres"   # Propietario de las BDs

need_file () {
  local f="$1"
  if [ ! -f "$f" ]; then
    echo "No existe el archivo: $f" >&2
    exit 1
  fi
}

ensure_db () {
  local db="$1"
  local owner="$2"
  # Crea la BD si no existe (UTF8, template0, owner) desde / para evitar permisos de cwd
  sudo -u postgres bash -lc "cd / && psql -tAc \"SELECT 1 FROM pg_database WHERE datname='${db}'\" | grep -q 1 || createdb -E UTF8 -T template0 -O ${owner} ${db}"
  # Asegura owner correcto
  sudo -u postgres bash -lc "cd / && psql -d ${db} -v ON_ERROR_STOP=1 -c \"ALTER DATABASE ${db} OWNER TO ${owner};\""
}

restore_sql () {
  local db="$1"
  local file="$2"
  echo "› Restaurando '${file}' en BD '${db}'..."
  # Ejecuta psql desde / y alimenta el SQL por stdin para evitar problemas de lectura
  sudo -u postgres bash -lc "cd / && psql --single-transaction -v ON_ERROR_STOP=1 -d \"${db}\"" < "${file}"
  echo "✓ Restauración completada (${db})"
}

main () {
  local sensor_path="${BACKUP_DIR}/${FILE_SENSOR}"
  local default_path="${BACKUP_DIR}/${FILE_DEFAULT}"

  need_file "$sensor_path"
  need_file "$default_path"

  echo "› Verificando/creando BDs..."
  ensure_db "$DB_SENSOR"  "$OWNER_ROLE"
  ensure_db "$DB_DEFAULT" "$OWNER_ROLE"

  restore_sql "$DB_SENSOR"  "$sensor_path"
  restore_sql "$DB_DEFAULT" "$default_path"

  echo "✔ Todo listo."
}

main "$@"
