#!/usr/bin/env bash
set -euo pipefail

# === Configurables (puedes dejarlos igual) ===
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_NAME="postgres"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
PORT="${PORT:-8080}"

# === Ubicación del proyecto (directorio donde está este script) ===
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

# === Verificación de privilegios (compatible con bash) ===
if [ "$(id -u)" -ne 0 ]; then
  echo "Por favor, ejecuta este script como superusuario: sudo bash install.sh"
  exit 1
fi

echo "Actualizando paquetes e instalando dependencias del SO..."
apt update -y && apt upgrade -y
apt install -y postgresql postgresql-contrib python3 python3-venv python3-pip

echo "Configurando PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql

# Evitar error de cwd cuando se cambia a usuario postgres
sudo -u postgres bash -lc "psql -tc 'SELECT 1' >/dev/null" || true

# Crear/actualizar rol de forma idempotente
sudo -u postgres bash -lc "psql <<'SQL'
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
      CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD' CREATEDB;
   ELSE
      ALTER ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD';
      ALTER ROLE $DB_USER CREATEDB;
   END IF;
END
\$\$;
SQL"

# Crear DB si no existe y asignar propietario
sudo -u postgres bash -lc "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='$DB_NAME'\" | grep -q 1 || createdb -O $DB_USER $DB_NAME"

echo "Base de datos '$DB_NAME' y usuario/rol '$DB_USER' verificados/creados."

echo "Configurando entorno virtual..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# Activar venv (bash)
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Actualizando pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "Instalando dependencias..."
if [ -f "$REQUIREMENTS_FILE" ]; then
  # Parche defensivo para NumPy 2.3.2 en Python 3.10 (no existe wheel compatible)
  if grep -q '^numpy==2\.3\.2$' "$REQUIREMENTS_FILE"; then
    sed -i 's/^numpy==2\.3\.2$/numpy==2.2.6/' "$REQUIREMENTS_FILE"
  fi
  pip install -r "$REQUIREMENTS_FILE"
else
  echo "Archivo $REQUIREMENTS_FILE no encontrado. Asegúrate de tenerlo en el directorio actual."
  deactivate || true
  exit 1
fi

echo "Cargando variables de entorno desde .env..."
if [ -f ".env" ]; then
  # Carga robusta (admite valores con espacios y evita romper PATH/IFS)
  set -a
  # shellcheck disable=SC1091
  . ".env"
  set +a
else
  echo "Archivo .env no encontrado. Asegúrate de tenerlo en el directorio actual."
  deactivate || true
  exit 1
fi

echo "Migrando base de datos de Django..."
python manage.py migrate --noinput

echo "Colectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando el servidor con Gunicorn (desde el venv)..."
# Lanza Gunicorn del venv; 'exec' reemplaza el proceso del script por Gunicorn
exec "$VENV_DIR/bin/gunicorn" --workers 3 --bind 0.0.0.0:"$PORT" core.wsgi:application
