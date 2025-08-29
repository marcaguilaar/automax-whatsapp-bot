import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()  # Cargar .env principal
load_dotenv('.env.whatsapp')  # Cargar configuración específica de WhatsApp

# Importar nuestros componentes del concesionario
from whatsapp_sender import WhatsAppSender
from message_manager import MessageManager
from car_dealership_agent import CarDealershipWhatsAppAgent

# Configuración de WhatsApp con validación
VERIFY_TOKEN_META = os.getenv("WHATSAPP_VERIFY_TOKEN", "automax_webhook_2025")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# Validar que las variables de entorno estén configuradas
if not WHATSAPP_ACCESS_TOKEN:
    print("❌ Error: WHATSAPP_ACCESS_TOKEN no está configurado")
    print("🔧 Configura la variable de entorno WHATSAPP_ACCESS_TOKEN")
    exit(1)

if not PHONE_NUMBER_ID:
    print("❌ Error: WHATSAPP_PHONE_NUMBER_ID no está configurado")
    print("🔧 Configura la variable de entorno WHATSAPP_PHONE_NUMBER_ID")
    exit(1)

# Inicializar componentes
whatsapp_sender = WhatsAppSender(WHATSAPP_ACCESS_TOKEN, PHONE_NUMBER_ID)
car_agent = CarDealershipWhatsAppAgent()
message_manager = MessageManager(whatsapp_sender, car_agent)

# Crear la app Flask
app = Flask(__name__)
CORS(app)

# Almacenamiento temporal en memoria (después será Firestore)
user_conversations = {}

@app.route('/', methods=['GET'])
def hello():
    return "🚗 AutoMax WhatsApp Bot - Sistema de Concesionario", 200

@app.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """
    Webhook principal para recibir mensajes de WhatsApp
    """
    if request.method == "GET":
        # Verificación del webhook de Meta
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if token == VERIFY_TOKEN_META:
            print("✅ Webhook verificado correctamente")
            return challenge
        else:
            print("❌ Token de verificación incorrecto")
            return "Token incorrecto", 403
    
    elif request.method == "POST":
        # Procesar mensajes entrantes
        try:
            data = request.json
            print(f"📨 Webhook POST recibido: {json.dumps(data, indent=2)}")
            
            # Verificar que sea un mensaje válido
            if not data or "entry" not in data:
                return jsonify({"status": "ok"})
            
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages":
                            process_whatsapp_message(change["value"])
            
            return jsonify({"status": "ok"})
            
        except Exception as e:
            print(f"❌ Error procesando webhook: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "method not allowed"}), 405

def process_whatsapp_message(message_data):
    """
    Procesa un mensaje individual de WhatsApp
    """
    try:
        # Extraer información del mensaje
        if "messages" not in message_data:
            return
        
        messages = message_data["messages"]
        contacts = message_data.get("contacts", [])
        
        for message in messages:
            # Información del usuario
            user_phone = message["from"]
            message_id = message["id"]
            timestamp = message["timestamp"]
            
            # Nombre del usuario (si está disponible)
            user_name = None
            for contact in contacts:
                if contact["wa_id"] == user_phone:
                    user_name = contact["profile"]["name"]
                    break
            
            print(f"📱 Mensaje de {user_name or user_phone}: {message_id}")
            
            # Procesar diferentes tipos de mensaje
            if message["type"] == "text":
                text_content = message["text"]["body"]
                print(f"💬 Texto: {text_content}")
                
                # Procesar mensaje de texto de forma síncrona
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        message_manager.handle_text_message(
                            user_phone=user_phone,
                            user_name=user_name,
                            message_text=text_content,
                            message_id=message_id
                        )
                    )
                    loop.close()
                    print(f"✅ Mensaje procesado: {result}")
                except Exception as e:
                    print(f"❌ Error procesando mensaje: {str(e)}")
                
            elif message["type"] == "interactive":
                # Procesar botones/respuestas interactivas
                interactive_data = message["interactive"]
                
                if interactive_data["type"] == "button_reply":
                    button_id = interactive_data["button_reply"]["id"]
                    button_title = interactive_data["button_reply"]["title"]
                    
                    print(f"🔘 Botón presionado: {button_id} - {button_title}")
                    
                    try:
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            message_manager.handle_interactive_message(
                                user_phone=user_phone,
                                user_name=user_name,
                                button_id=button_id,
                                button_title=button_title,
                                message_id=message_id
                            )
                        )
                        loop.close()
                        print(f"✅ Botón procesado: {result}")
                    except Exception as e:
                        print(f"❌ Error procesando botón: {str(e)}")
                
                elif interactive_data["type"] == "list_reply":
                    list_id = interactive_data["list_reply"]["id"]
                    list_title = interactive_data["list_reply"]["title"]
                    
                    print(f"📋 Lista seleccionada: {list_id} - {list_title}")
                    
                    message_manager.handle_list_selection(
                        user_phone=user_phone,
                        user_name=user_name,
                        selection_id=list_id,
                        selection_title=list_title,
                        message_id=message_id
                    )
            
            elif message["type"] == "image":
                # Procesar imágenes (futuro: fotos de autos que quieren)
                image_id = message["image"]["id"]
                caption = message["image"].get("caption", "")
                
                print(f"🖼️ Imagen recibida: {image_id} - {caption}")
                
                message_manager.handle_image_message(
                    user_phone=user_phone,
                    user_name=user_name,
                    image_id=image_id,
                    caption=caption,
                    message_id=message_id
                )
            
            else:
                print(f"❓ Tipo de mensaje no soportado: {message['type']}")
                
    except Exception as e:
        print(f"❌ Error procesando mensaje: {str(e)}")

@app.route('/status', methods=['GET'])
def status():
    """
    Endpoint para verificar el estado del sistema
    """
    return jsonify({
        "status": "active",
        "service": "AutoMax WhatsApp Bot",
        "version": "1.0.0",
        "active_conversations": len(user_conversations),
        "components": {
            "whatsapp_sender": "ready",
            "car_agent": "ready",
            "message_manager": "ready"
        }
    })

@app.route('/test', methods=['POST'])
def test_message():
    """
    Endpoint para probar mensajes sin WhatsApp (desarrollo)
    """
    try:
        data = request.json
        user_phone = data.get("phone", "test_user")
        message_text = data.get("message", "Hola")
        user_name = data.get("name", "Usuario Test")
        
        print(f"🧪 Mensaje de prueba de {user_name}: {message_text}")
        
        # Simular procesamiento del mensaje
        response = message_manager.handle_text_message(
            user_phone=user_phone,
            user_name=user_name,
            message_text=message_text,
            message_id="test_" + str(int(time.time()))
        )
        
        return jsonify({
            "status": "success",
            "user": user_phone,
            "message_sent": message_text,
            "response": response
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    print("🚗 Iniciando AutoMax WhatsApp Bot...")
    print(f"📱 Phone Number ID: {PHONE_NUMBER_ID}")
    print(f"🔑 Access Token configurado: {'✅' if WHATSAPP_ACCESS_TOKEN else '❌'}")
    print(f"🔐 Verify Token: {VERIFY_TOKEN_META}")
    
    # Configuración para desarrollo local
    app.run(host='127.0.0.1', port=8080, debug=True)
