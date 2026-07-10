# Alerts ETL - Webhook a GCP

Este proyecto contiene una Google Cloud Function diseñada para recibir webhooks (por ejemplo, alertas de New Relic) y procesarlos dentro de Google Cloud Platform (GCP).

## Arquitectura

- **Tecnología**: Google Cloud Functions (Gen 2) / Cloud Run
- **Lenguaje**: Python 3.10+
- **Trigger**: HTTP
- **CI/CD**: Despliegue automatizado mediante GitHub Actions

## Estructura del Proyecto

- `main.py`: Contiene el punto de entrada de la aplicación, específicamente la función `receive_webhook` que maneja las solicitudes HTTP entrantes.
- `requirements.txt`: Lista de dependencias de Python (ej. `functions-framework`, `google-cloud-pubsub`, etc.).
- `.github/workflows/deploy.yml`: Pipeline de CI/CD que se encarga de empaquetar y desplegar el código en GCP de manera automática cuando hay un `push` a la rama `main`.
- `.gitignore`: Evita que archivos sensibles (como claves JSON y entornos virtuales) se suban al repositorio.

## Cómo funciona el despliegue automático

El despliegue está automatizado con GitHub Actions. Cuando integras un cambio a la rama `main`, ocurre lo siguiente:

1. **GitHub Actions** detecta el cambio e inicia el pipeline definido en `.github/workflows/deploy.yml`.
2. Se autentica en Google Cloud utilizando las credenciales almacenadas en el secreto de GitHub `GCP_CREDENTIALS`.
3. Ejecuta el comando `gcloud functions deploy`, indicando que se trata de una función de 2ª Generación (`--gen2`).
4. **Google Cloud Build** toma el código fuente y el `requirements.txt`, construye un contenedor Docker transparente para nosotros y lo guarda en **Artifact Registry**.
5. Finalmente, el contenedor se despliega y ejecuta sobre **Cloud Run**.

## Configuración y Permisos (Service Account)

Para que GitHub Actions pueda realizar este despliegue exitosamente en GCP (especialmente al usar Gen 2), la **Cuenta de Servicio (Service Account)** configurada en el secreto `GCP_CREDENTIALS` necesita los siguientes roles de IAM:

1. **Cloud Functions Developer** (`roles/cloudfunctions.developer`): Para crear y actualizar la Cloud Function.
2. **Cloud Run Developer** (`roles/run.developer`): Requerido porque las funciones Gen 2 corren sobre Cloud Run.
3. **Cloud Build Editor** (`roles/cloudbuild.builds.editor`): Para construir el contenedor a partir del código fuente.
4. **Artifact Registry Writer** (`roles/artifactregistry.writer`): Para guardar la imagen del contenedor generada.
5. **Service Account User** (`roles/iam.serviceAccountUser`): Para permitir que la Cloud Function asuma su propia identidad de ejecución.

## Ejecución Local

Para probar la función localmente antes de desplegar, asegúrate de tener un entorno virtual y usar `functions-framework`:

```bash
python -m venv .venv
source .venv/Scripts/activate  # En Windows
pip install -r requirements.txt
functions-framework --target=receive_webhook --port=8080
```
Luego puedes enviar peticiones HTTP de prueba a `http://localhost:8080`.
