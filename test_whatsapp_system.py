#!/usr/bin/env python3
"""
Script de prueba para el sistema de WhatsApp de AutoMax
"""

import asyncio
import json
import requests
import time
from whatsapp_sender import WhatsAppSender
from car_dealership_agent import CarDealershipWhatsAppAgent
from message_manager import MessageManager

# Configuración para pruebas
TEST_PHONE = "test_user_123"
TEST_ACCESS_TOKEN = "test_token"
TEST_PHONE_NUMBER_ID = "test_phone_id"

async def test_whatsapp_system():
    """
    Prueba el sistema completo de WhatsApp sin necesidad de API real
    """
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA WHATSAPP AUTOMAX")
    print("=" * 60)
    
    # Crear instancias (modo prueba)
    sender = WhatsAppSender(TEST_ACCESS_TOKEN, TEST_PHONE_NUMBER_ID)
    agent = CarDealershipWhatsAppAgent()
    message_manager = MessageManager(sender, agent)
    
    # Test 1: Mensaje de bienvenida
    print("\n📝 TEST 1: Mensaje de bienvenida")
    print("-" * 40)
    
    result = await message_manager.handle_text_message(
        user_phone=TEST_PHONE,
        user_name="Usuario Test",
        message_text="Hola",
        message_id="test_msg_1"
    )
    
    print(f"Resultado: {result}")
    
    # Test 2: Búsqueda de auto económico
    print("\n📝 TEST 2: Búsqueda de auto económico")
    print("-" * 40)
    
    result = await message_manager.handle_text_message(
        user_phone=TEST_PHONE,
        user_name="Usuario Test",
        message_text="Busco un auto económico",
        message_id="test_msg_2"
    )
    
    print(f"Resultado: {result}")
    
    # Test 3: Pregunta por BMW
    print("\n📝 TEST 3: Pregunta por BMW")
    print("-" * 40)
    
    result = await message_manager.handle_text_message(
        user_phone=TEST_PHONE,
        user_name="Usuario Test", 
        message_text="¿Tienen BMW disponibles?",
        message_id="test_msg_3"
    )
    
    print(f"Resultado: {result}")
    
    # Test 4: Botón interactivo
    print("\n📝 TEST 4: Botón interactivo")
    print("-" * 40)
    
    result = await message_manager.handle_interactive_message(
        user_phone=TEST_PHONE,
        user_name="Usuario Test",
        button_id="search_cars",
        button_title="Buscar autos",
        message_id="test_msg_4"
    )
    
    print(f"Resultado: {result}")
    
    # Test 5: Agendar cita
    print("\n📝 TEST 5: Agendar cita")
    print("-" * 40)
    
    result = await message_manager.handle_text_message(
        user_phone=TEST_PHONE,
        user_name="Usuario Test",
        message_text="Quiero agendar una cita",
        message_id="test_msg_5"
    )
    
    print(f"Resultado: {result}")
    
    # Test 6: Información de contacto
    print("\n📝 TEST 6: Información de contacto")
    print("-" * 40)
    
    result = await message_manager.handle_interactive_message(
        user_phone=TEST_PHONE,
        user_name="Usuario Test",
        button_id="contact_info",
        button_title="Contacto",
        message_id="test_msg_6"
    )
    
    print(f"Resultado: {result}")
    
    # Mostrar resumen de la conversación
    print("\n📊 RESUMEN DE LA CONVERSACIÓN")
    print("-" * 40)
    
    conversation = agent.get_user_history(TEST_PHONE)
    print(f"Total de mensajes: {len(conversation)}")
    
    for i, msg in enumerate(conversation, 1):
        role_emoji = "🧑" if msg["role"] == "user" else "🤖"
        print(f"{i}. {role_emoji} {msg['role']}: {msg['content'][:50]}...")
    
    summary = agent.get_conversation_summary(TEST_PHONE)
    print(f"\nResumen: {summary}")
    
    print("\n✅ PRUEBAS COMPLETADAS")
    print("=" * 60)

def test_webhook_simulation():
    """
    Simula un webhook de WhatsApp
    """
    print("\n🔗 SIMULANDO WEBHOOK DE WHATSAPP")
    print("-" * 40)
    
    # Simular datos de webhook de WhatsApp
    webhook_data = {
        "entry": [{
            "changes": [{
                "field": "messages",
                "value": {
                    "messages": [{
                        "from": "521234567890",
                        "id": "wamid.test123",
                        "timestamp": str(int(time.time())),
                        "type": "text",
                        "text": {
                            "body": "Hola, busco un auto"
                        }
                    }],
                    "contacts": [{
                        "wa_id": "521234567890",
                        "profile": {
                            "name": "Juan Pérez"
                        }
                    }]
                }
            }]
        }]
    }
    
    print("Datos del webhook:")
    print(json.dumps(webhook_data, indent=2))
    
    # En un entorno real, esto se enviaría a http://localhost:8080/whatsapp
    print("\n💡 Para probar con webhook real:")
    print("1. Ejecuta: python whatsapp_main.py")
    print("2. Usa ngrok para exponer el puerto: ngrok http 8080")
    print("3. Configura la URL del webhook en Meta Business")

def test_api_endpoints():
    """
    Prueba los endpoints de la API (requiere que el servidor esté corriendo)
    """
    print("\n🌐 PROBANDO ENDPOINTS DE LA API")
    print("-" * 40)
    
    base_url = "http://localhost:8080"
    
    # Test endpoint de status
    try:
        response = requests.get(f"{base_url}/status")
        print(f"Status endpoint: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
    except requests.exceptions.ConnectionError:
        print("❌ Servidor no está ejecutándose. Ejecuta: python whatsapp_main.py")
        return
    
    # Test endpoint de prueba
    test_message = {
        "phone": "521234567890",
        "message": "Hola, busco un BMW",
        "name": "Usuario Test API"
    }
    
    try:
        response = requests.post(f"{base_url}/test", json=test_message)
        print(f"\nTest endpoint: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Error probando endpoint: {str(e)}")

def main():
    """
    Ejecuta todas las pruebas
    """
    print("🚗 AUTOMAX WHATSAPP - SUITE DE PRUEBAS")
    print("=" * 60)
    
    # Pruebas asíncronas del sistema
    asyncio.run(test_whatsapp_system())
    
    # Simulación de webhook
    test_webhook_simulation()
    
    # Pruebas de API (opcional)
    print("\n❓ ¿Quieres probar los endpoints de la API? (servidor debe estar corriendo)")
    respuesta = input("Escribe 'si' para probar o Enter para omitir: ").lower()
    
    if respuesta in ['si', 'sí', 's', 'yes', 'y']:
        test_api_endpoints()
    
    print("\n🎉 ¡TODAS LAS PRUEBAS COMPLETADAS!")
    print("\n💡 Para ejecutar el servidor:")
    print("   python whatsapp_main.py")
    print("\n📱 Para conectar con WhatsApp real:")
    print("   1. Obtén tokens de Meta Business")
    print("   2. Actualiza .env.whatsapp")
    print("   3. Configura webhook en Meta")

if __name__ == "__main__":
    main()
