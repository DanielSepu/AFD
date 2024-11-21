<<<<<<< HEAD
# VentApp

plataforma web para el control de la solución Auxiliary Fan Device AFD

[![Built with Django Bootstrap Template](https://img.shields.io/badge/Built%20with-Django%20Bootstrap%20Template-blueviolet.svg)](https://github.com/griceturrble/django-bootstrap-template/) [![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


## License

This project uses the MIT license. Please see the [LICENSE](LICENSE) for details.


## Installation

1. Create a new Python virtual environment.

   - Using `venv` on Linux:

     ```bash
     python3 -m venv .venv --prompt ventapp
     ```

   - Using `venv` on Windows:

     ```bash
     python3 -m venv .venv --prompt ventapp
     ```

   - Or, use whichever style of virtual environment management you prefer!

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

1. *PostgreSQL settings*: if not present already create a new `.env` file at `ventapp/core/.env`. This file should be gitignored from the repo, and should contain credentials for connecting to the PostgreSQL database:

   - `POSTGRES_NAME`: database name
   - `POSTGRES_USER`: username
   - `POSTGRES_PASSWORD`: password
   - `POSTGRES_HOST`: host serving the database
   - `POSTGRES_PORT`: port

1. Migrate models to the database:

   ```bash
   python ventapp/manage.py migrate
   ```

1. Create a superuser:

   ```bash
   python ventapp/manage.py createsuperuser
   ```

1. Run the development server:

   ```bash
   python ventapp/manage.py runserver
   ```

1. Open http://localhost:8000 to view the running site.
=======
> [!NOTE]
> features
> 1. se corrigio error en la seccion de agregar a base de datos. seccion ventilador, se pueden agregar nuevos accesorios
> 2. correccion de gestion cuando no hay proyectos activos
> 3. se agrego el campo id que no permite actualizar el proyecto actual

> [!IMPORTANT]
> en la seccion de nuevo proyecto, los campos caudal requerido, curva de diseño y area galeria estaban solo de lectura sin ningun valor por default, por lo que se desbloqueo para que sea un campo editable,
> queda pendiente revisar si debe ser de solo lectura y de donde saldra el valor por defector para estos campos.
>>>>>>> 935ff88b7adb741504f4e4aaec1f423f300afca2
