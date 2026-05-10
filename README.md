# Stealth Honeypot API & Threat Logger

Una API de engaño (deception) diseñada para capturar, clasificar y analizar intentos de intrusión en tiempo real. Este proyecto actúa como una capa de monitoreo defensivo que identifica patrones de ataque comunes (Bot scans, SQLi, Brute Force) antes de que lleguen a sistemas críticos.

## Características Técnicas (Key Features)

- **Honey-Endpoints**: Implementación de rutas "trampa" (`/admin/config`, `/.env`, `/wp-admin`, `/v1/auth/login`) para atraer bots y atacantes automatizados.
- **Threat Classifier**: Motor de detección basado en Expresiones Regulares (Regex) para identificar inyecciones SQL y escaneos de vulnerabilidades o Path Traversal.
- **Active Defense**: Sistema de Rate Limiting y bloqueo temporal de IPs basado en comportamiento malicioso para mitigar ataques continuos.
- **Invisible Logging**: Registro asíncrono de ataques en base de datos mediante Background Tasks en FastAPI, evitando alertar al atacante con latencias inusuales.
- **Intelligence Dashboard**: Endpoint protegido por API Key (Custom Headers) para extraer métricas analíticas de los ataques capturados (Top IPs, Clasificación de Amenazas).

## Guía de Instalación Paso a Paso

1. Clona el repositorio en tu máquina local:
   ```bash
   git clone https://github.com/javierd1408/honeypot-api.git
   cd honeypot-api
   ```

2. Configura las variables de entorno. Copia el archivo de ejemplo y ajusta la `ADMIN_API_KEY`:
   ```bash
   cp .env.example .env
   ```

3. Levanta la infraestructura (API + PostgreSQL) utilizando Docker Compose:
   ```bash
   docker-compose up --build -d
   ```

La API estará escuchando silenciosamente en `http://localhost:8000`.

## Cómo Probar el Honeypot (Demo Flow)

Con los contenedores en ejecución, puedes simular diferentes escenarios de ataque.

**1. Escaneo de Bots (Buscando archivos sensibles)**
```bash
curl -v http://localhost:8000/.env
```
*(El sistema responderá con un error HTTP común para engañar al bot, pero lo registrará como `BOT_SCAN`)*

**2. Ataque de Inyección SQL (SQLi)**
```bash
curl -X POST http://localhost:8000/v1/auth/login -H "Content-Type: application/json" -d "{\"username\": \"admin' OR 1=1--\", \"password\": \"123\"}"
```
*(El sistema simulará un fallo de autenticación, pero el Threat Classifier atrapará el payload malicioso como `SQL_INJECTION_ATTEMPT`)*

**3. Trigger de Bloqueo (Rate Limiting en acción)**
Realiza 6 peticiones seguidas al endpoint `/.env`. A la sexta petición, el sistema de Defensa Activa bloqueará tu IP y recibirás un:
```json
{"detail": "Too Many Requests"}
```

**4. Ver la Inteligencia Recolectada**
Usa tu API Key como administrador para acceder al dashboard y ver los resultados de tus ataques:
```bash
curl -H "X-Admin-Token: super-secret-admin-token-change-me" http://localhost:8000/api/v1/intruders
```

## Ethical Use (Advertencia Legal y Ética)

> [!WARNING]
> Este proyecto ha sido desarrollado **exclusivamente con fines educativos y de investigación en ciberseguridad**. Su propósito es demostrar conceptos de Threat Intelligence y Deception Technology.
> No debe ser desplegado en entornos de producción en internet abierto sin la implementación de medidas de seguridad de infraestructura adicionales (Proxies inversos, Hardening de contenedores, Redes aisladas). El despliegue irresponsable de Honeypots puede atraer actores maliciosos reales a tu red. Úsalo bajo tu propia responsabilidad.
