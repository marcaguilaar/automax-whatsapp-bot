const dotenv = require('dotenv');
const { CarDealershipChatAgent } = require('./chat-agent');

// Cargar variables de entorno
dotenv.config();

// Crear instancia del agente
const agent = new CarDealershipChatAgent();

// Tests específicos para temas que suelen causar alucinaciones
const strictTests = [
  {
    query: "¿Qué garantía tiene el Toyota Camry?",
    prohibited: ["generalmente", "típicamente", "toyota ofrece", "normalmente", "usualmente", "años o", "millas"]
  },
  {
    query: "¿Cuál es la tasa de interés del financiamiento?",
    prohibited: ["generalmente", "típicamente", "normalmente", "usualmente", "entre", "aproximadamente"]
  },
  {
    query: "¿El BMW incluye seguro?",
    prohibited: ["generalmente", "típicamente", "normalmente", "usualmente", "incluye", "no incluye"]
  },
  {
    query: "¿Hacen descuentos por pago de contado?",
    prohibited: ["generalmente", "típicamente", "normalmente", "usualmente", "ofrecemos", "hacemos"]
  }
];

async function testStrictNoHallucination() {
  console.log('🔒 PRUEBAS ESTRICTAS ANTI-ALUCINACIÓN');
  console.log('='.repeat(60));
  
  for (let i = 0; i < strictTests.length; i++) {
    const test = strictTests[i];
    
    console.log(`\n📝 TEST ${i + 1}: ${test.query}`);
    console.log('-'.repeat(50));
    
    try {
      const response = await agent.chat(test.query);
      console.log(`🤖 Respuesta: ${response}`);
      
      // Verificar palabras prohibidas
      const foundProhibited = test.prohibited.filter(phrase => 
        response.toLowerCase().includes(phrase.toLowerCase())
      );
      
      if (foundProhibited.length > 0) {
        console.log(`❌ ALUCINACIÓN DETECTADA! Palabras prohibidas: ${foundProhibited.join(', ')}`);
      } else {
        console.log('✅ Respuesta parece estrictamente basada en datos del sistema');
      }
      
      // Verificar si menciona correctamente los límites del sistema
      const goodPhrases = [
        'no tengo esa información',
        'no tengo información específica',
        'contactar directamente',
        'nuestro sistema'
      ];
      
      const hasGoodLimits = goodPhrases.some(phrase => 
        response.toLowerCase().includes(phrase.toLowerCase())
      );
      
      if (hasGoodLimits) {
        console.log('✅ Reconoce apropiadamente sus limitaciones');
      }
      
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
    }
    
    console.log('='.repeat(60));
    
    // Pausa entre tests
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  console.log('\n🏁 PRUEBAS ESTRICTAS COMPLETADAS');
  console.log('💡 El agente debe rechazar preguntas sobre info que no tiene en el sistema');
}

// Ejecutar las pruebas
testStrictNoHallucination().catch(console.error);
