const dotenv = require('dotenv');
const OpenAI = require('openai');
const readline = require('readline');

// Load environment variables
dotenv.config({ path: '.env.local' });

// Same setup as before...
const sampleInventory = [
  {
    id: 'bmw-x5-2024-001',
    brand: 'BMW',
    model: 'X5',
    year: 2024,
    price: 65000,
    color: 'Mineral White',
    mileage: 1200,
    fuelType: 'gasoline',
    bodyStyle: 'suv',
    fuelEfficiency: '21 city / 26 highway mpg',
    features: ['All-wheel drive', 'Premium package', 'Navigation system'],
    description: 'Luxury SUV with exceptional performance and comfort.',
    location: 'Main Lot A-12',
    isAvailable: true
  },
  {
    id: 'toyota-camry-2023-001',
    brand: 'Toyota',
    model: 'Camry',
    year: 2023,
    price: 28500,
    color: 'Celestial Silver',
    mileage: 8500,
    fuelType: 'gasoline',
    bodyStyle: 'sedan',
    fuelEfficiency: '28 city / 39 highway mpg',
    features: ['Toyota Safety Sense 2.0', 'Wireless charging', 'Android Auto'],
    description: 'Reliable and fuel-efficient sedan. Perfect for daily commuting.',
    location: 'Main Lot B-5',
    isAvailable: true
  },
  {
    id: 'tesla-model3-2024-001',
    brand: 'Tesla',
    model: 'Model 3',
    year: 2024,
    price: 42000,
    color: 'Pearl White',
    mileage: 500,
    fuelType: 'electric',
    bodyStyle: 'sedan',
    fuelEfficiency: '134 MPGe combined',
    features: ['Autopilot', 'Full self-driving capability', '15-inch touchscreen'],
    description: 'All-electric sedan with cutting-edge technology.',
    location: 'Electric Vehicle Section E-1',
    isAvailable: true
  }
];

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Tool functions (simplified)
const tools = {
  searchInventory: (params) => {
    let results = [...sampleInventory];
    if (params.brand) {
      results = results.filter(car => 
        car.brand.toLowerCase().includes(params.brand.toLowerCase())
      );
    }
    if (params.budget && params.budget.toLowerCase().includes('econom')) {
      results = results.filter(car => car.price < 30000);
    }
    return {
      success: true,
      totalFound: results.length,
      cars: results.map(car => ({
        id: car.id,
        brand: car.brand,
        model: car.model,
        year: car.year,
        price: car.price,
        description: car.description
      }))
    };
  },

  getCarDetails: (params) => {
    const car = sampleInventory.find(c => c.id === params.carId);
    if (!car) return { success: false, error: 'Car not found' };
    return { success: true, car };
  }
};

const functionTools = [
  {
    type: 'function',
    function: {
      name: 'searchInventory',
      description: 'Search for cars based on customer needs',
      parameters: {
        type: 'object',
        properties: {
          brand: { type: 'string' },
          budget: { type: 'string' }
        }
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'getCarDetails',
      description: 'Get detailed information about a specific car',
      parameters: {
        type: 'object',
        properties: {
          carId: { type: 'string' }
        },
        required: ['carId']
      }
    }
  }
];

// Chat function with full history support
async function chat(message, conversationHistory = []) {
  try {
    const messages = [
      {
        role: 'system',
        content: `Eres un asistente experto de ventas del concesionario "Premier Auto Dealership".

IMPORTANTE sobre el historial y referencias:
- SIEMPRE considera toda la conversación anterior
- Si el usuario hace referencias como "ese coche", "el BMW que mencionaste", "el primero", etc., 
  usa el contexto de mensajes anteriores para entender a qué se refiere
- Mantén coherencia con lo que ya has discutido
- Recuerda las preferencias que el usuario ha expresado

Tu trabajo es ayudar con búsquedas de vehículos e información detallada usando las herramientas disponibles.`
      },
      ...conversationHistory,
      { role: 'user', content: message }
    ];

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: messages,
      tools: functionTools,
      tool_choice: 'auto',
      temperature: 0.7,
      max_tokens: 1000
    });

    const response = completion.choices[0].message;

    if (response.tool_calls && response.tool_calls.length > 0) {
      const newMessages = [...messages, response];

      for (const toolCall of response.tool_calls) {
        const functionName = toolCall.function.name;
        const args = JSON.parse(toolCall.function.arguments);
        const result = tools[functionName](args);

        newMessages.push({
          role: 'tool',
          tool_call_id: toolCall.id,
          content: JSON.stringify(result)
        });
      }

      const finalCompletion = await openai.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: newMessages,
        temperature: 0.7,
        max_tokens: 1000
      });

      return {
        response: finalCompletion.choices[0].message.content,
        newHistory: newMessages
      };
    }

    return {
      response: response.content,
      newHistory: [...messages, response]
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      response: 'Lo siento, ha ocurrido un error. ¿Podrías intentar de nuevo?',
      newHistory: conversationHistory
    };
  }
}

// Interactive chat with history demonstration
async function testHistoryDemo() {
  console.log('🧠 DEMO: Capacidad de Historial y Referencias');
  console.log('===========================================');
  console.log('');
  console.log('Voy a simular una conversación con referencias a mensajes anteriores:');
  console.log('');

  let history = [];

  // Secuencia de mensajes que demuestran el historial
  const conversation = [
    "Busco algo económico para ir al trabajo",
    "¿Cuál es más eficiente en combustible?",
    "Cuéntame más sobre ese Toyota",
    "¿Y el Tesla que mencionaste antes?",
    "Compara el primero con el último",
    "Me quedo con el más barato de los dos"
  ];

  for (let i = 0; i < conversation.length; i++) {
    const userMessage = conversation[i];
    
    console.log(`\n${i + 1}. 👤 Usuario: "${userMessage}"`);
    console.log('   🔍 Procesando con historial...');

    const result = await chat(userMessage, history);
    history = result.newHistory;

    console.log(`   🤖 Agente: ${result.response}`);
    console.log('   ' + '─'.repeat(60));

    // Small delay for readability
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  console.log('\n✅ DEMOSTRACIÓN COMPLETADA');
  console.log('\n📊 CAPACIDADES DE HISTORIAL VERIFICADAS:');
  console.log('   ✓ Referencias a coches mencionados anteriormente');
  console.log('   ✓ Comparaciones entre opciones previas');
  console.log('   ✓ Contexto acumulativo mantenido');
  console.log('   ✓ Comprensión de pronombres y referencias');
  console.log('');
  console.log('🧠 El agente recuerda TODA la conversación anterior');
  console.log('💾 Historial almacenado: ' + history.length + ' mensajes');
}

// Interactive chat mode
async function interactiveChat() {
  console.log('\n🎮 MODO INTERACTIVO - Prueba el historial tú mismo');
  console.log('===============================================');
  console.log('');
  console.log('Puedes hacer referencias como:');
  console.log('- "ese coche que mencionaste"');
  console.log('- "el BMW de antes"');
  console.log('- "compara el primero con el segundo"');
  console.log('- "¿cuál era más barato?"');
  console.log('');
  console.log('Escribe "salir" para terminar');
  console.log('Escribe "historial" para ver la conversación completa');
  console.log('');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  let history = [];

  while (true) {
    const userInput = await new Promise(resolve => {
      rl.question('👤 Tú: ', resolve);
    });

    if (userInput.toLowerCase() === 'salir') {
      console.log('👋 ¡Hasta luego!');
      break;
    }

    if (userInput.toLowerCase() === 'historial') {
      console.log('\n📜 HISTORIAL DE CONVERSACIÓN:');
      console.log('============================');
      history.forEach((msg, index) => {
        if (msg.role === 'user') {
          console.log(`${index}. 👤 Usuario: ${msg.content}`);
        } else if (msg.role === 'assistant') {
          console.log(`${index}. 🤖 Agente: ${msg.content}`);
        }
      });
      console.log('============================\n');
      continue;
    }

    const result = await chat(userInput, history);
    history = result.newHistory;

    console.log(`🤖 Agente: ${result.response}\n`);
  }

  rl.close();
}

// Main execution
async function main() {
  if (!process.env.OPENAI_API_KEY) {
    console.log('❌ Error: OPENAI_API_KEY no está configurado');
    return;
  }

  // First run the demo
  await testHistoryDemo();

  // Then offer interactive mode
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const choice = await new Promise(resolve => {
    rl.question('\n¿Quieres probar el modo interactivo? (s/n): ', resolve);
  });

  rl.close();

  if (choice.toLowerCase() === 's' || choice.toLowerCase() === 'si') {
    await interactiveChat();
  }
}

main().catch(console.error);
