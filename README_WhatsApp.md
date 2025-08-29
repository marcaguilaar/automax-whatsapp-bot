# 🚗 AutoMax WhatsApp Bot - Sistema de Concesionario

Sistema completo de WhatsApp Business API para concesionario de automóviles AutoMax.

## 📋 Características

- ✅ **Chat inteligente** con IA para consultas sobre automóviles
- ✅ **Botones interactivos** para navegación fácil
- ✅ **Búsqueda de inventario** por tipo, marca, precio
- ✅ **Agendamiento de citas** para pruebas de manejo
- ✅ **Información de contacto** y ubicación
- ✅ **Historial de conversación** por usuario
- ✅ **Respuestas contextuales** basadas en la conversación

## 🏗️ Arquitectura

```
whatsapp_main.py          # Servidor Flask principal
├── message_manager.py    # Coordinador de mensajes
├── whatsapp_sender.py    # Cliente de WhatsApp API
├── car_dealership_agent.py # Agente del concesionario
└── test_whatsapp_system.py # Suite de pruebas
```

## 🚀 Instalación y Configuración

### 1. Dependencias

```bash
pip install flask flask-cors python-dotenv requests
```

### 2. Configuración de WhatsApp

1. **Crear aplicación en Meta Business:**
   - Ve a [developers.facebook.com](https://developers.facebook.com)
   - Crea una nueva aplicación de WhatsApp Business
   - Obtén tu `Access Token` y `Phone Number ID`

2. **Configurar variables de entorno:**
   
   Crea un archivo `.env.whatsapp`:
   ```env
   WHATSAPP_ACCESS_TOKEN=tu_access_token_aqui
   WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id_aqui
   WHATSAPP_VERIFY_TOKEN=automax_verify_token_12345
   ```

### 3. Ejecutar el sistema

```bash
# Ejecutar el servidor
python whatsapp_main.py

# En otra terminal, ejecutar pruebas
python test_whatsapp_system.py
```

## 📱 Configuración del Webhook

### Para desarrollo local con ngrok:

1. **Instalar ngrok:**
   ```bash
   # macOS
   brew install ngrok
   
   # O descargar desde https://ngrok.com
   ```

2. **Exponer puerto local:**
   ```bash
   ngrok http 8080
   ```

3. **Configurar webhook en Meta:**
   - URL: `https://tu-url-ngrok.ngrok.io/whatsapp`
   - Verify Token: `automax_verify_token_12345`

## 🧪 Pruebas

### Pruebas automáticas:
```bash
python test_whatsapp_system.py
```

### Pruebas manuales:
```bash
# Con el servidor corriendo, prueba:
curl -X POST http://localhost:8080/test \
  -H "Content-Type: application/json" \
  -d '{"phone": "521234567890", "message": "Hola", "name": "Test User"}'
```

## 💬 Comandos de WhatsApp

### Comandos de usuario:
- `/menu` - Mostrar menú principal  
- `/ayuda` - Mostrar ayuda
- `/reiniciar` - Reiniciar conversación

### Botones interactivos:
- **🔍 Buscar autos** - Búsqueda por tipo/marca
- **📅 Agendar cita** - Pruebas de manejo, consultas
- **📞 Contacto** - Información y ubicación

### Ejemplos de consultas:
- "Busco un auto económico"
- "¿Qué BMWs tienen disponibles?"
- "Quiero agendar una prueba de manejo"
- "¿Cuáles son sus horarios?"

## 📊 Endpoints de la API

### `GET /`
Página de inicio

### `GET /whatsapp` 
Verificación del webhook

### `POST /whatsapp`
Recepción de mensajes de WhatsApp

### `GET /status`
Estado del sistema
```json
{
  "status": "active",
  "service": "AutoMax WhatsApp Bot",
  "active_conversations": 5,
  "components": {
    "whatsapp_sender": "ready",
    "car_agent": "ready"
  }
}
```

### `POST /test`
Endpoint de pruebas
```json
{
  "phone": "521234567890",
  "message": "Hola",
  "name": "Test User"
}
```

## 🔧 Componentes Principales

### WhatsAppSender
- Envío de mensajes de texto
- Botones interactivos (máximo 3)
- Listas de selección
- Imágenes y ubicaciones
- Información de contacto

### MessageManager
- Procesamiento de mensajes entrantes
- Coordinación entre WhatsApp y el agente
- Gestión de flujos de conversación
- Comandos especiales

### CarDealershipWhatsAppAgent
- Lógica del concesionario
- Análisis de respuestas del IA
- Gestión de historial por usuario
- Estados de conversación

## 🎯 Flujos de Conversación

### 1. Usuario nuevo:
```
Usuario: "Hola"
Bot: Mensaje de bienvenida + botones del menú
```

### 2. Búsqueda de autos:
```
Usuario: Presiona "🔍 Buscar autos"
Bot: Botones de tipo (Económico/Familiar/Lujo)
Usuario: Selecciona tipo
Bot: Resultados del inventario + opciones
```

### 3. Agendamiento:
```
Usuario: "Quiero agendar una cita"
Bot: Tipos de cita (Prueba/Consulta/Inspección)
Usuario: Selecciona tipo
Bot: Procesa con el agente IA
```

## 🔮 Próximas Funcionalidades

- [ ] **Integración con Firestore** para persistencia
- [ ] **Multi-tenant** para múltiples concesionarios
- [ ] **Imágenes de vehículos** en respuestas
- [ ] **Calculadora de financiamiento** interactiva
- [ ] **Notificaciones proactivas** de nuevos inventarios
- [ ] **Integración con CRM** existente

## 🐛 Resolución de Problemas

### Error: "Token de verificación incorrecto"
- Verifica que `WHATSAPP_VERIFY_TOKEN` coincida en `.env` y Meta Business

### Error: "Connection refused"
- Asegúrate de que el servidor esté corriendo en puerto 8080
- Verifica que ngrok esté exponiendo el puerto correcto

### Error: "Access token inválido"
- Renueva el token en Meta Business
- Actualiza `WHATSAPP_ACCESS_TOKEN` en `.env`

### Los botones no aparecen:
- WhatsApp solo permite máximo 3 botones por mensaje
- Verifica que el formato JSON sea correcto

## 📞 Soporte

Para problemas o preguntas:
- 📧 Email: soporte@automax.com
- 📱 WhatsApp: +52 123 456 7890
- 🌐 Web: www.automax.com

---
**AutoMax** - Tu concesionario de confianza 🚗✨
