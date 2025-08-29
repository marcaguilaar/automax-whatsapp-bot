# 🔑 Guía Completa: Cómo Obtener Tokens de WhatsApp Business

## 📋 **Resumen: ¿Qué necesitas obtener?**

```bash
WHATSAPP_ACCESS_TOKEN=EAABsBCS...     # Token de Meta (24h temporal)
WHATSAPP_PHONE_NUMBER_ID=123...       # ID del número de teléfono
WHATSAPP_VERIFY_TOKEN=mi_secreto      # Token que tú defines
```

---

## 🚀 **Proceso Paso a Paso**

### **PASO 1: Crear Aplicación en Meta**

1. **Ve a**: https://developers.facebook.com
2. **Inicia sesión** con tu cuenta de Facebook
3. **Clic en**: "My Apps" → "Create App"
4. **Selecciona**: "Business" 
5. **Completa**:
   - App name: "AutoMax WhatsApp Bot"
   - App contact email: tu email
   - Business account: Selecciona o crea uno

### **PASO 2: Agregar WhatsApp Business**

1. **En tu app nueva**, clic en "Add Products"
2. **Busca "WhatsApp"** → clic "Set up"
3. **Acepta términos** de WhatsApp Business
4. **Configura perfil empresarial**:
   - Nombre: AutoMax
   - Descripción: Concesionario de autos
   - Sitio web: (opcional)

### **PASO 3: Obtener PHONE_NUMBER_ID**

```
📱 Ubicación: WhatsApp → API Setup → "From" field
📋 Formato: 15 dígitos (ej: 123456789012345)
📝 Copia este número - es tu WHATSAPP_PHONE_NUMBER_ID
```

### **PASO 4: Obtener ACCESS_TOKEN (Temporal)**

```
🔑 Ubicación: WhatsApp → API Setup → "Temporary access token"
⏰ Duración: 24 horas
📝 Copia el token completo (EAABsBCS...)
```

**⚠️ IMPORTANTE**: Este token expira en 24 horas. Para producción necesitas uno permanente.

### **PASO 5: Definir VERIFY_TOKEN**

```
🔐 Tú lo defines: Cualquier string secreto
💡 Ejemplo: "automax_webhook_2025"
📝 Guárdalo - lo necesitas para el webhook
```

---

## 🔧 **Configuración en tu Sistema**

### **Actualizar .env.whatsapp**

Edita el archivo `.env.whatsapp` con tus valores reales:

```bash
# Reemplaza con tus valores reales de Meta
WHATSAPP_ACCESS_TOKEN=EAABsBCS1234567890abcdef...
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=automax_webhook_2025
```

### **Exponer tu Servidor (ngrok)**

⚠️ **IMPORTANTE**: ngrok gratuito cambia la URL cada vez. Aquí las opciones:

#### **Opción A: ngrok Gratuito (URL cambia cada vez)**
```bash
# Terminal 1: Ejecutar tu servidor
python whatsapp_main.py

# Terminal 2: Exponer con ngrok
ngrok http 8080

# Resultado: https://abc123.ngrok.io (cambia cada vez)
```

#### **Opción B: ngrok con Cuenta (URL fija)**
```bash
# 1. Crear cuenta en https://ngrok.com (gratis)
# 2. Obtener authtoken y configurar:
ngrok config add-authtoken tu_authtoken

# 3. Usar subdominio gratuito:
ngrok http 8080 --subdomain=automax-2025

# Resultado: https://automax-2025.ngrok.io (siempre igual)
```

#### **Opción C: Solo para Desarrollo**
```bash
# Ejecutar normalmente y actualizar webhook manualmente
ngrok http 8080
# Copiar URL nueva cada vez y actualizar en Meta Developer Console
```

### **Configurar Webhook en Meta**

⚠️ **Con ngrok gratuito**: Necesitas actualizar esto cada vez que reinicies ngrok

1. **Ve a**: WhatsApp → Configuration → Webhook
2. **Callback URL**: `https://abc123.ngrok.io/webhook` (usar URL actual de ngrok)
3. **Verify token**: Tu WHATSAPP_VERIFY_TOKEN
4. **Webhook fields**: Marca "messages"
5. **Clic "Verify and save"**

💡 **Tip**: Copia la URL HTTPS que aparece en la terminal de ngrok

---

## 🔄 **Flujo de Desarrollo Diario**

### **Cada vez que quieras desarrollar:**

```bash
# 1. Iniciar servidor
python whatsapp_main.py

# 2. En otra terminal, iniciar ngrok
ngrok http 8080

# 3. Copiar la URL HTTPS (ej: https://xyz789.ngrok.io)
# 4. Ir a Meta Developer Console
# 5. Actualizar webhook: https://xyz789.ngrok.io/webhook
# 6. Verificar y guardar
```

### **Soluciones para URL Fija:**

#### **A. ngrok con Cuenta Gratuita + Subdomain**
```bash
# Registrarse en https://ngrok.com
# Obtener authtoken gratuito
ngrok config add-authtoken tu_authtoken

# Usar subdomain fijo (plan gratuito permite 1)
ngrok http 8080 --subdomain=automax-dev
# URL: https://automax-dev.ngrok.io (siempre igual)
```

#### **B. Alternativas Gratuitas**
- **LocalTunnel**: `npx localtunnel --port 8080 --subdomain automax`
- **Serveo**: `ssh -R automax:80:localhost:8080 serveo.net`
- **Cloudflare Tunnel**: Gratuito con dominio fijo

#### **C. VPS para Desarrollo ($5/mes)**
- **Railway**: Deploy automático desde GitHub
- **DigitalOcean**: VPS simple
- **Heroku**: Free tier (limitado)

---

## 🧪 **Probar con Número Real**

### **Configurar Número de Prueba**

1. **En Meta**: WhatsApp → API Setup
2. **"To" field**: Agrega tu número personal
3. **Formato**: +52 1 234 567 8901 (con código país)

### **Enviar Mensaje de Prueba**

1. **En el panel de Meta**, usa "Send Message"
2. **O envía** un WhatsApp a tu número de negocio
3. **Tu bot debería responder** con el sistema AutoMax

---

## 🔒 **Token Permanente (Producción)**

Para un token que no expire:

### **Crear System User**

1. **Ve a**: Business Settings → System Users
2. **Clic**: "Add System User"
3. **Nombre**: "AutoMax WhatsApp Bot"
4. **Role**: Admin

### **Generar Token Permanente**

1. **Selecciona** tu System User
2. **Clic**: "Generate New Token"
3. **App**: Selecciona tu app AutoMax
4. **Permisos**: Marca `whatsapp_business_messaging`
5. **Expira**: "Never" (nunca)
6. **Guarda** este token - es permanente

---

## 🎯 **Verificar que Todo Funciona**

### **Test 1: Status del Bot**
```bash
curl http://localhost:8080/status
```

### **Test 2: Webhook Verification**
```bash
# Meta automáticamente probará tu webhook
# Verifica en logs que aparezca "Webhook verified"
```

### **Test 3: Mensaje Real**
```
1. Envía "Hola" por WhatsApp a tu número de negocio
2. El bot debe responder con bienvenida de AutoMax
3. Prueba "Busco un BMW" → Debe mostrar inventario
```

---

## ❌ **Problemas Comunes**

### **Error 401: Invalid Access Token**
```
❌ Problema: Token expirado o incorrecto
✅ Solución: Obtén nuevo token temporal o crea permanente
```

### **Error 400: Invalid Phone Number**
```
❌ Problema: Formato incorrecto de número
✅ Solución: Usa formato +52XXXXXXXXXX
```

### **Webhook No Funciona**
```
❌ Problema: URL no accesible
✅ Solución: Verifica ngrok está corriendo y URL es correcta
```

### **Sin Respuestas del Bot**
```
❌ Problema: Webhook no configurado
✅ Solución: Verifica callback URL y verify token
```

---

## 📱 **Números de Teléfono**

### **Para Desarrollo**
- Usa tu número personal
- Máximo 5 números de prueba
- Gratis para testing

### **Para Producción**
- Verifica tu número de negocio
- Proceso de aprobación de Meta
- Puede tomar 1-3 días

---

## 💰 **Costos**

### **WhatsApp Business API**
- Mensajes de bienvenida: Gratis
- Respuestas (24h): Gratis  
- Mensajes iniciados: ~$0.005-0.015 USD c/u

### **Infraestructura**
- OpenAI API: ~$15-150/mes según volumen
- Servidor: ~$5-20/mes (VPS básico)
- ngrok Pro (opcional): $8/mes

---

## 🎉 **¡Listo para Producción!**

Una vez configurado:

1. ✅ **Tokens reales** configurados
2. ✅ **Webhook** verificado  
3. ✅ **Número aprobado** por Meta
4. ✅ **Servidor** en VPS (no local)
5. ✅ **Dominio propio** (opcional)

Tu AutoMax WhatsApp Bot estará **100% operativo** para clientes reales.

---

**📞 ¿Necesitas ayuda?** 
- Meta Business Help: https://business.facebook.com/help
- WhatsApp Business API Docs: https://developers.facebook.com/docs/whatsapp
