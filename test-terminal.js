import { carDealershipAgent } from '../src/app/agentConfigs/carDealership/index.js';
import readline from 'readline';

// Simple terminal test for the car dealership agent
async function testCarDealershipAgent() {
  console.log('🚗 Car Dealership Agent Test Terminal');
  console.log('=====================================');
  console.log('Puedes hacer preguntas como:');
  console.log('- "Busco un coche económico para ir al trabajo"');
  console.log('- "¿Qué BMWs tienen disponibles?"');
  console.log('- "Cuéntame más sobre el Tesla Model 3"');
  console.log('- "¿A qué hora abren?"');
  console.log('- "Quiero agendar una cita para probar un coche"');
  console.log('=====================================\n');

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

    try {
      console.log('\n🤖 Agente: Procesando tu consulta...\n');
      
      // Here we would normally use the OpenAI API to process the message
      // For now, let's show what tools would be available
      console.log('Herramientas disponibles para este agente:');
      carDealershipAgent.tools?.forEach((tool, index) => {
        console.log(`${index + 1}. ${tool.name} - ${tool.description}`);
      });
      
      console.log('\n💡 En una implementación completa, el agente analizaría tu mensaje:');
      console.log(`"${userInput}"`);
      console.log('Y usaría las herramientas apropiadas para responderte.\n');
      
    } catch (error) {
      console.error('Error:', error);
    }
  }

  rl.close();
}

// Run the test
testCarDealershipAgent().catch(console.error);
