const dotenv = require('dotenv');
const { CarDealershipChatAgent } = require('./chat-agent');

// Cargar variables de entorno
dotenv.config();

// Crear instancia del agente
const agent = new CarDealershipChatAgent();

// Tests específicos para verificar que no alucine
const testQueries = [
  {
    query: "¿Tienen un Ferrari disponible?",
    expectation: "Debería buscar en inventario y reportar que no hay Ferraris"
  },
  {
    query: "¿Cuánto cuesta el BMW más barato?",
    expectation: "Debería buscar BMWs en inventario y dar precio real"
  },
  {
    query: "¿Tienen promociones especiales este mes?", 
    expectation: "Debería decir que no tiene esa información específica"
  },
  {
    query: "¿El Toyota Camry tiene garantía de 10 años?",
    expectation: "Debería obtener info del Camry real, pero no inventar datos de garantía"
  },
  {
    query: "¿Qué tal está el mercado de autos usado este año?",
    expectation: "Debería redirigir a información que sí tiene disponible"
  }
];

async function testNoHallucination() {
  console.log('🧪 PRUEBAS ANTI-ALUCINACIÓN DEL AGENTE AUTOMAX');
  console.log('='.repeat(60));
  
  for (let i = 0; i < testQueries.length; i++) {
    const test = testQueries[i];
    
    console.log(`\n📝 TEST ${i + 1}: ${test.query}`);
    console.log(`🎯 Expectativa: ${test.expectation}`);
    console.log('-'.repeat(50));
    
    try {
      const response = await agent.chat(test.query);
      console.log(`🤖 Respuesta: ${response}`);
      
      // Verificar si menciona información que no debería tener
      const problematicPhrases = [
        'probablemente',
        'generalmente',
        'usualmente',
        'típicamente',
        'en mi experiencia',
        'según mi conocimiento',
        'normalmente'
      ];
      
      const hasProblematic = problematicPhrases.some(phrase => 
        response.toLowerCase().includes(phrase)
      );
      
      if (hasProblematic) {
        console.log('⚠️  ADVERTENCIA: Posible alucinación detectada');
      } else {
        console.log('✅ Respuesta parece basada en datos reales');
      }
      
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
    }
    
    console.log('='.repeat(60));
    
    // Pausa entre tests para no saturar la API
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  console.log('\n🏁 PRUEBAS COMPLETADAS');
  console.log('💡 Revisa las respuestas para confirmar que solo usa información real del inventario');
}

// Ejecutar las pruebas
testNoHallucination().catch(console.error);
