const readline = require('readline');
const dotenv = require('dotenv');
const { CarDealershipChatAgent } = require('./chat-agent');

// Cargar variables de entorno
dotenv.config();

// Configurar interfaz de readline para input del usuario
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Crear instancia del agente
const agent = new CarDealershipChatAgent();

// Estado de la conversación
let conversationHistory = [];

// Función para mostrar el prompt del usuario
function showPrompt() {
  process.stdout.write('\n🚗 Tú: ');
}

// Función para mostrar respuesta del agente
function showAgentResponse(response) {
  console.log(`\n🤖 Agente AutoMax: ${response}\n`);
}

// Función para mostrar información del sistema
function showSystemInfo(info) {
  console.log(`\n💡 Sistema: ${info}`);
}

// Función principal de chat
async function chat(userMessage) {
  try {
    // Agregar mensaje del usuario al historial
    conversationHistory.push({
      role: 'user',
      content: userMessage
    });

    // Obtener respuesta del agente
    const response = await agent.chat(userMessage, conversationHistory);
    
    // Agregar respuesta del agente al historial
    conversationHistory.push({
      role: 'assistant',
      content: response
    });

    return response;
  } catch (error) {
    console.error('Error en el chat:', error);
    return 'Lo siento, hubo un error procesando tu mensaje. ¿Puedes intentar de nuevo?';
  }
}

// Función para mostrar comandos especiales
function showHelp() {
  console.log(`
📋 Comandos especiales:
- /help - Mostrar esta ayuda
- /historial - Ver el historial de conversación
- /limpiar - Limpiar historial de conversación
- /salir - Terminar el chat
- /estado - Mostrar estado de la conversación

💬 Ejemplos de preguntas:
- "Busco un auto económico"
- "¿Qué autos híbridos tienen?"
- "Quiero agendar una cita"
- "¿Cuáles son sus horarios?"
- "Me interesa financiamiento"
- "Compara el Corolla con el Civic"
`);
}

// Función para mostrar el historial
function showHistory() {
  console.log('\n📜 Historial de conversación:');
  console.log('=' .repeat(50));
  
  conversationHistory.forEach((message, index) => {
    const role = message.role === 'user' ? '🚗 Tú' : '🤖 Agente';
    const content = message.content.length > 100 
      ? message.content.substring(0, 100) + '...' 
      : message.content;
    
    console.log(`${index + 1}. ${role}: ${content}`);
  });
  
  console.log('=' .repeat(50));
  console.log(`Total de mensajes: ${conversationHistory.length}`);
}

// Función para mostrar estado
function showStatus() {
  console.log('\n📊 Estado de la conversación:');
  console.log(`- Mensajes en historial: ${conversationHistory.length}`);
  console.log(`- Agente inicializado: ✅`);
  console.log(`- API Key configurada: ${process.env.OPENAI_API_KEY ? '✅' : '❌'}`);
}

// Función para limpiar historial
function clearHistory() {
  conversationHistory = [];
  console.log('\n🧹 Historial de conversación limpiado');
}

// Función para procesar comandos especiales
function processCommand(input) {
  const command = input.toLowerCase().trim();
  
  switch(command) {
    case '/help':
      showHelp();
      return true;
    case '/historial':
      showHistory();
      return true;
    case '/limpiar':
      clearHistory();
      return true;
    case '/estado':
      showStatus();
      return true;
    case '/salir':
      console.log('\n👋 ¡Gracias por visitar AutoMax! Que tengas un buen día.\n');
      rl.close();
      return true;
    default:
      return false;
  }
}

// Función principal para manejar input del usuario
function handleUserInput(input) {
  const trimmedInput = input.trim();
  
  // Verificar si es un comando especial
  if (trimmedInput.startsWith('/')) {
    processCommand(trimmedInput);
    showPrompt();
    return;
  }
  
  // Si no hay input, mostrar prompt nuevamente
  if (!trimmedInput) {
    showPrompt();
    return;
  }
  
  // Procesar mensaje normal
  showSystemInfo('Procesando tu mensaje...');
  
  chat(trimmedInput)
    .then(response => {
      showAgentResponse(response);
      showPrompt();
    })
    .catch(error => {
      console.error('\n❌ Error:', error.message);
      showPrompt();
    });
}

// Función de inicialización
async function initialize() {
  console.clear();
  
  // Banner de bienvenida
  console.log(`
🚗 ═══════════════════════════════════════════════════ 🚗
    🏢 BIENVENIDO AL CHAT INTERACTIVO DE AUTOMAX 🏢
🚗 ═══════════════════════════════════════════════════ 🚗

¡Hola! Soy tu asistente virtual de AutoMax, el concesionario
de autos más confiable de la ciudad.

🔧 Puedo ayudarte con:
• Buscar el auto perfecto para ti
• Información detallada de vehículos
• Agendar citas de prueba
• Opciones de financiamiento
• Horarios y ubicación
• Promociones especiales

💬 Escribe tu mensaje o usa /help para ver comandos especiales
`);

  // Verificar configuración
  if (!process.env.OPENAI_API_KEY) {
    console.log('❌ Error: No se encontró OPENAI_API_KEY en las variables de entorno');
    console.log('Por favor, configura tu API key en el archivo .env\n');
    rl.close();
    return;
  }

  showSystemInfo('Sistema inicializado correctamente ✅');
  
  // Mostrar primer prompt
  showPrompt();
  
  // Configurar listener para input del usuario
  rl.on('line', handleUserInput);
  
  // Manejar cierre del programa
  rl.on('close', () => {
    console.log('\n👋 Chat terminado. ¡Hasta la próxima!\n');
    process.exit(0);
  });
}

// Manejar errores no capturados
process.on('uncaughtException', (error) => {
  console.error('\n❌ Error crítico:', error.message);
  console.log('El chat se cerrará. Reinicia para continuar.\n');
  rl.close();
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('\n❌ Error no manejado:', reason);
  console.log('Continuando con el chat...\n');
  showPrompt();
});

// Inicializar el chat
initialize();
