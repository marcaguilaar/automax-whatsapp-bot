import { CarDealershipChatAgent } from './src/app/agentConfigs/carDealership/chat-agent.js';
import readline from 'readline';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: '.env.local' });

// Simple terminal test for the car dealership chat agent
async function testCarDealershipChatAgent() {
  console.log('🚗 Car Dealership Chat Agent Test');
  console.log('==================================');
  
  // Check if API key is configured
  if (!process.env.OPENAI_API_KEY) {
    console.log('❌ Error: OPENAI_API_KEY no está configurado');
    console.log('Por favor, crea un archivo .env.local con:');
    console.log('OPENAI_API_KEY=tu_api_key_aqui');
    console.log('\n💡 Este agente usa Chat Completions API (mucho más barata que Realtime)');
    console.log('Costos aproximados:');
    console.log('- GPT-4o-mini: $0.15/1M tokens input, $0.60/1M tokens output');
    console.log('- vs Realtime API: $6.00/minute');
    console.log('= ~95% más económico para chat 💰');
    return;
  }

  console.log('✅ API Key configurado');
  console.log('💰 Usando Chat Completions API (95% más barato que Realtime)');
  console.log('\nPuedes hacer preguntas como:');
  console.log('- "Busco un coche económico para ir al trabajo"');
  console.log('- "¿Qué BMWs tienen disponibles?"');
  console.log('- "Cuéntame más sobre el Tesla Model 3"');
  console.log('- "¿A qué hora abren?"');
  console.log('- "Quiero agendar una cita para probar un coche"');
  console.log('\nEscribe "salir" para terminar');
  console.log('=====================================\n');

  const agent = new CarDealershipChatAgent();

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  while (true) {
    const userInput = await new Promise(resolve => {
      rl.question('Usuario: ', resolve);
    });

    if (userInput.toLowerCase() === 'salir' || userInput.toLowerCase() === 'exit') {
      console.log('¡Hasta luego!');
      break;
    }

    if (userInput.toLowerCase() === 'historial') {
      console.log('\n📝 Historial de conversación:');
      const history = agent.getHistory();
      history.forEach((msg, index) => {
        if (msg.role !== 'system') {
          console.log(`${index}. ${msg.role}: ${msg.content}`);
        }
      });
      console.log('');
      continue;
    }

    if (userInput.toLowerCase() === 'limpiar') {
      agent.clearHistory();
      console.log('🧹 Historial limpiado\n');
      continue;
    }

    try {
      console.log('\n🤖 Agente: Procesando...');
      const response = await agent.chat(userInput);
      console.log(`\n🤖 Agente: ${response}\n`);
      
    } catch (error) {
      console.error('❌ Error:', error.message);
      console.log('');
    }
  }

  rl.close();
}

// Show cost comparison
console.log('💰 COMPARACIÓN DE COSTOS:');
console.log('========================');
console.log('Realtime API (con voz):');
console.log('  - $6.00 por minuto');
console.log('  - Para 1 hora de chat: ~$360');
console.log('');
console.log('Chat Completions API (solo texto):');
console.log('  - GPT-4o-mini: $0.15/1M tokens input');
console.log('  - Para conversación típica: ~$0.01-0.05');
console.log('  - Para 1 hora de chat: ~$0.50-2.00');
console.log('');
console.log('🎯 AHORRO: ~95-99% menos costo');
console.log('========================\n');

// Run the test
testCarDealershipChatAgent().catch(console.error);
