#!/bin/bash
echo "🔧 Instalando dependencias de Node.js..."
npm install

echo "🔧 Instalando dependencias de Python..."
pip install -r requirements.txt

echo "✅ Build completado"
