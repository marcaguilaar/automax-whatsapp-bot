#!/bin/bash
# Script para automatizar el setup de desarrollo WhatsApp

echo "🚀 INICIANDO DESARROLLO WHATSAPP AUTOMAX"
echo "========================================="

# 1. Verificar que el servidor esté listo
if [ ! -f "whatsapp_main.py" ]; then
    echo "❌ Error: whatsapp_main.py no encontrado"
    exit 1
fi

# 2. Iniciar servidor en background
echo "📡 Iniciando servidor Flask..."
python whatsapp_main.py &
SERVER_PID=$!

# Esperar a que el servidor inicie
sleep 3

# 3. Verificar que el servidor está corriendo
if curl -s http://localhost:8080/status > /dev/null; then
    echo "✅ Servidor iniciado correctamente"
else
    echo "❌ Error: Servidor no responde"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# 4. Iniciar ngrok
echo "🌐 Iniciando ngrok..."
echo "⚠️  IMPORTANTE: Copia la URL HTTPS que aparece"
echo "⚠️  Ve a Meta Developer Console y actualiza el webhook"
echo ""
echo "📝 URL del webhook será: https://XXXXX.ngrok.io/webhook"
echo "🔑 Token de verificación: automax_verify_token_12345"
echo ""
echo "Presiona Ctrl+C para detener todo"

# Capturar Ctrl+C para limpiar procesos
trap 'echo ""; echo "🛑 Deteniendo servicios..."; kill $SERVER_PID 2>/dev/null; exit 0' INT

# Ejecutar ngrok
ngrok http 8080
