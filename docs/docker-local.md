# Docker y despliegue en AWS Academy

`compose.yaml` levanta Nginx (Gateway), Django con gunicorn, Flask con gunicorn, PostgreSQL y Redis. Django ejecuta las migraciones y el seed no destructivo al arrancar. Los datos quedan en el volumen `vaultdrop-pgdata`, que se conserva al detener los contenedores.

## Local

Copiar `.env.example` a `.env` y llenar `DJANGO_SECRET_KEY` y `POSTGRES_PASSWORD` con `openssl rand -hex 32`. Compose no arranca si están vacíos.

```sh
cp .env.example .env
docker compose up --build -d
docker compose exec web python manage.py test apps --noinput
docker compose down
```

Si el puerto 80 está ocupado, usar por ejemplo `HTTP_PORT=8002` en `.env`.

## EC2

1. En AWS Academy, crear una instancia Ubuntu 24.04 (mínimo 2 GB de RAM, por ejemplo `t3.small`).
2. En su Security Group, abrir el puerto 22 solo para su IP y el 80 para todos.
3. Crear una IP elástica y asociarla a la instancia.
4. Entrar por SSH e instalar Docker:

   ```sh
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose-v2 git
   sudo systemctl enable --now docker
   sudo usermod -aG docker ubuntu
   ```

5. Cerrar y volver a abrir la sesión SSH, y luego clonar y configurar:

   ```sh
   git clone https://github.com/jrestrepoc/VaultDrop.git
   cd VaultDrop
   cp .env.example .env
   nano .env
   ```

   En `.env`, generar los secretos con `openssl rand -hex 32` y agregar la IP elástica a `DJANGO_ALLOWED_HOSTS`.

6. Levantar y verificar:

   ```sh
   docker compose up --build -d
   docker compose ps
   curl http://<IP-ELASTICA>/api/v1/cajas/
   curl http://<IP-ELASTICA>/api/v2/catalogo/
   ```

Los contenedores usan `restart: unless-stopped`, así que vuelven solos cuando se enciende la instancia. El laboratorio de AWS Academy la apaga al terminar la sesión: debe estar encendida durante la sustentación.

## Límites

El tráfico va por HTTP, sin TLS. Una sola instancia con la base de datos en un contenedor no ofrece alta disponibilidad ni copias de seguridad.
