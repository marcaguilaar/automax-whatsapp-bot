# Deploy en Render - WhatsApp Bot

## Pasos para hacer deploy en Render

### 1. Preparar el repositorio
- Asegúrate de que tu código esté en un repositorio de GitHub
- Los archivos necesarios ya están creados: `requirements.txt`, `Procfile`, `start_server.py`

### 2. Crear cuenta en Render
- Ve a [render.com](https://render.com)
- Crea una cuenta gratuita
- Conecta tu cuenta de GitHub

### 3. Crear un nuevo Web Service
1. Click en "New +" > "Web Service"
2. Conecta tu repositorio de GitHub
3. Configurar el servicio:
   - **Name**: `automax-whatsapp-bot`
   - **Region**: Cualquiera cercana a tu ubicación
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_server.py`

### 4. Variables de Entorno
En la sección "Environment" de tu servicio, agregar:

```
WHATSAPP_ACCESS_TOKEN=tu_token_real_aqui
WHATSAPP_PHONE_NUMBER_ID=794726787054146
WHATSAPP_VERIFY_TOKEN=automax_webhook_2025
OPENAI_API_KEY=tu_openai_key_aqui
FLASK_ENV=production
FLASK_DEBUG=False
```

### 5. Deploy
- Click en "Create Web Service"
- Render automáticamente hará el build y deploy
- Te dará una URL como: `https://automax-whatsapp-bot.onrender.com`

### 6. Configurar webhook en Meta
1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Tu app > WhatsApp > Configuration
3. Cambiar webhook URL a: `https://tu-app.onrender.com/whatsapp`
4. Verificar webhook con token: `automax_webhook_2025`

### 7. Pruebas
- El bot estará disponible 24/7
- Render mantiene el servicio activo automáticamente
- Los logs están disponibles en el dashboard de Render

## Características del deploy:

✅ **Gratis**: Render ofrece 750 horas gratuitas por mes
✅ **SSL automático**: HTTPS incluido
✅ **Auto-deploy**: Se actualiza automáticamente cuando haces push al repo
✅ **Logs**: Monitoreo completo de la aplicación
✅ **Escalable**: Puede manejar múltiples usuarios simultáneos

## Limitaciones del plan gratuito:
- El servicio puede "dormirse" después de 15 minutos de inactividad
- Se "despierta" automáticamente cuando recibe una request
- Para uso 24/7 sin interrupciones, considera el plan pago ($7/mes)

## Troubleshooting:
- Si hay errores, revisa los logs en el dashboard de Render
- Verifica que todas las variables de entorno estén configuradas
- Asegúrate de que la URL del webhook sea correcta en Meta Developer Console
