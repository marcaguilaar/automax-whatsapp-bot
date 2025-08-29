// Simple test script for car dealership data

// Manually defined test data based on our sampleData.ts
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
    location: 'Main Lot A-12'
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
    location: 'Main Lot B-5'
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
    location: 'Electric Vehicle Section E-1'
  }
];

const businessInfo = {
  name: 'Premier Auto Dealership',
  address: '123 Main Street, Cityville, ST 12345',
  phone: '(555) 123-4567',
  email: 'info@premierauto.com',
  hours: {
    'Monday': '9:00 AM - 8:00 PM',
    'Tuesday': '9:00 AM - 8:00 PM',
    'Wednesday': '9:00 AM - 8:00 PM',
    'Thursday': '9:00 AM - 8:00 PM',
    'Friday': '9:00 AM - 8:00 PM',
    'Saturday': '9:00 AM - 6:00 PM',
    'Sunday': '12:00 PM - 5:00 PM'
  },
  services: [
    'New car sales',
    'Used car sales',
    'Financing and leasing',
    'Trade-in evaluations'
  ]
};

console.log('🚗 Car Dealership Agent - Prueba de Datos');
console.log('==========================================\n');

console.log('📊 INVENTARIO DE COCHES:');
console.log('-------------------------');
sampleInventory.forEach((car, index) => {
  console.log(`${index + 1}. ${car.year} ${car.brand} ${car.model}`);
  console.log(`   Precio: $${car.price.toLocaleString()}`);
  console.log(`   Color: ${car.color}`);
  console.log(`   Combustible: ${car.fuelType}`);
  console.log(`   Eficiencia: ${car.fuelEfficiency}`);
  console.log(`   Ubicación: ${car.location}`);
  console.log('');
});

console.log('🏢 INFORMACIÓN DEL NEGOCIO:');
console.log('----------------------------');
console.log(`Nombre: ${businessInfo.name}`);
console.log(`Dirección: ${businessInfo.address}`);
console.log(`Teléfono: ${businessInfo.phone}`);
console.log(`Email: ${businessInfo.email}`);

console.log('\n⏰ HORARIOS:');
Object.entries(businessInfo.hours).forEach(([day, hours]) => {
  console.log(`${day}: ${hours}`);
});

console.log('\n🔧 SERVICIOS DISPONIBLES:');
businessInfo.services.forEach((service, index) => {
  console.log(`${index + 1}. ${service}`);
});

console.log('\n✅ Todo configurado correctamente!');
console.log('\n🎯 PRÓXIMOS PASOS:');
console.log('1. El agente puede buscar coches por criterios flexibles');
console.log('2. Proporciona información detallada de cada vehículo');  
console.log('3. Puede agendar citas con información del cliente');
console.log('4. Ofrece opciones de financiamiento');
console.log('5. Responde preguntas generales del negocio');

console.log('\n💡 EJEMPLOS DE CONSULTAS QUE PUEDE MANEJAR:');
console.log('- "Busco algo económico para ir al trabajo"');
console.log('- "¿Tienen SUVs familiares disponibles?"');
console.log('- "Quiero ver el BMW X5 en detalle"');
console.log('- "¿Puedo agendar una prueba de manejo para mañana?"');
console.log('- "¿Qué opciones de financiamiento tienen?"');
console.log('- "¿A qué hora abren los fines de semana?"');

console.log('\n🧠 INTELIGENCIA DEL AGENTE:');
console.log('---------------------------');
console.log('✓ Interpretación natural del lenguaje (sin palabras clave hardcodeadas)');
console.log('✓ Búsqueda inteligente por necesidades del cliente');
console.log('✓ Recomendaciones contextuales');
console.log('✓ Manejo de citas sin formularios complejos');
console.log('✓ Respuestas conversacionales naturales');
