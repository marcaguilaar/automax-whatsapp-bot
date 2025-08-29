#!/usr/bin/env python3
"""
Script para verificar la configuración antes del deploy
"""

import os
from dotenv import load_dotenv

def check_config():
    print("🔍 Verificando configuración para deploy...")
    
    # Cargar variables de entorno
    load_dotenv()
    load_dotenv('.env.whatsapp')
    
    errors = []
    warnings = []
    
    # Verificar variables obligatorias
    required_vars = {
        'WHATSAPP_ACCESS_TOKEN': 'Token de acceso de WhatsApp Business API',
        'WHATSAPP_PHONE_NUMBER_ID': 'ID del número de teléfono de WhatsApp',
        'WHATSAPP_VERIFY_TOKEN': 'Token de verificación del webhook',
        'OPENAI_API_KEY': 'Clave API de OpenAI'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ {var} no está configurado ({description})")
        else:
            # Verificar longitud para detectar tokens de ejemplo
            if var in ['WHATSAPP_ACCESS_TOKEN', 'OPENAI_API_KEY'] and len(value) < 20:
                warnings.append(f"⚠️  {var} parece ser un valor de ejemplo (muy corto)")
            else:
                print(f"✅ {var}: {'*' * 8}...{value[-4:] if len(value) > 4 else '***'}")
    
    # Verificar archivos necesarios
    required_files = [
        'requirements.txt',
        'Procfile', 
        'start_server.py',
        'whatsapp_main.py',
        'chat-agent.js'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} existe")
        else:
            errors.append(f"❌ {file} no encontrado")
    
    # Verificar que Node.js esté disponible
    import subprocess
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js disponible: {result.stdout.strip()}")
        else:
            warnings.append("⚠️  Node.js no disponible - necesario para el chat agent")
    except FileNotFoundError:
        warnings.append("⚠️  Node.js no encontrado - necesario para el chat agent")
    
    # Mostrar resultados
    print("\n" + "="*50)
    
    if warnings:
        print("⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"   {warning}")
        print()
    
    if errors:
        print("❌ ERRORES que deben corregirse:")
        for error in errors:
            print(f"   {error}")
        print("\n🔧 Corrige estos errores antes del deploy.")
        return False
    else:
        print("✅ ¡Configuración lista para deploy!")
        print("\n📋 Próximos pasos:")
        print("1. Haz push de tu código a GitHub")
        print("2. Crea un Web Service en Render.com")
        print("3. Configura las variables de entorno en Render")
        print("4. Actualiza la URL del webhook en Meta Developer Console")
        return True

if __name__ == "__main__":
    check_config()
