// Sample data for the car dealership

// Sample car inventory
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
    transmission: 'automatic',
    engineSize: '3.0L I6 Turbo',
    fuelEfficiency: '21 city / 26 highway mpg',
    features: [
      'All-wheel drive',
      'Premium package',
      'Navigation system',
      'Leather seats',
      'Panoramic sunroof',
      'Harman Kardon sound system',
      'Apple CarPlay',
      'Lane departure warning'
    ],
    description: 'Luxury SUV with exceptional performance and comfort. Perfect for families who want style and capability.',
    images: ['bmw-x5-1.jpg', 'bmw-x5-2.jpg'],
    isAvailable: true,
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
    transmission: 'automatic',
    engineSize: '2.5L 4-Cylinder',
    fuelEfficiency: '28 city / 39 highway mpg',
    features: [
      'Toyota Safety Sense 2.0',
      'Wireless charging',
      'Android Auto',
      'Apple CarPlay',
      'Dual-zone climate control',
      'Backup camera',
      'Blind spot monitoring'
    ],
    description: 'Reliable and fuel-efficient sedan. Perfect for daily commuting with excellent safety ratings.',
    images: ['toyota-camry-1.jpg', 'toyota-camry-2.jpg'],
    isAvailable: true,
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
    transmission: 'automatic',
    engineSize: 'Electric Motor',
    fuelEfficiency: '134 MPGe combined',
    features: [
      'Autopilot',
      'Full self-driving capability',
      '15-inch touchscreen',
      'Premium connectivity',
      'Supercharging network access',
      'Over-the-air updates',
      'Glass roof'
    ],
    description: 'All-electric sedan with cutting-edge technology and impressive range. Zero emissions driving.',
    images: ['tesla-model3-1.jpg', 'tesla-model3-2.jpg'],
    isAvailable: true,
    location: 'Electric Vehicle Section E-1'
  },
  {
    id: 'ford-f150-2023-001',
    brand: 'Ford',
    model: 'F-150',
    year: 2023,
    price: 45000,
    color: 'Antimatter Blue',
    mileage: 3200,
    fuelType: 'gasoline',
    bodyStyle: 'pickup',
    transmission: 'automatic',
    engineSize: '3.5L V6 EcoBoost',
    fuelEfficiency: '20 city / 24 highway mpg',
    features: [
      '4WD',
      'Towing package',
      'Bed liner',
      'SYNC 4 infotainment',
      'FordPass Connect',
      'Pro Trailer Backup Assist',
      'Multi-contour front seats'
    ],
    description: 'America\'s best-selling truck. Built tough for work and play with impressive towing capacity.',
    images: ['ford-f150-1.jpg', 'ford-f150-2.jpg'],
    isAvailable: true,
    location: 'Truck Section T-3'
  },
  {
    id: 'honda-civic-2024-001',
    brand: 'Honda',
    model: 'Civic',
    year: 2024,
    price: 24000,
    color: 'Rallye Red',
    mileage: 1800,
    fuelType: 'gasoline',
    bodyStyle: 'hatchback',
    transmission: 'manual',
    engineSize: '2.0L 4-Cylinder',
    fuelEfficiency: '31 city / 40 highway mpg',
    features: [
      'Honda Sensing suite',
      'Apple CarPlay',
      'Android Auto',
      '7-inch touchscreen',
      'Adaptive cruise control',
      'Collision mitigation',
      'Sport mode'
    ],
    description: 'Sporty and efficient compact car. Great for young drivers and city commuting.',
    images: ['honda-civic-1.jpg', 'honda-civic-2.jpg'],
    isAvailable: true,
    location: 'Compact Section C-7'
  },
  {
    id: 'audi-a4-2023-001',
    brand: 'Audi',
    model: 'A4',
    year: 2023,
    price: 38000,
    color: 'Glacier White',
    mileage: 5500,
    fuelType: 'gasoline',
    bodyStyle: 'sedan',
    transmission: 'automatic',
    engineSize: '2.0L Turbo',
    fuelEfficiency: '24 city / 31 highway mpg',
    features: [
      'Quattro AWD',
      'Virtual cockpit',
      'MMI infotainment',
      'Premium Plus package',
      'Sunroof',
      'Bang & Olufsen sound',
      'Audi pre sense'
    ],
    description: 'German luxury sedan with sophisticated technology and premium materials.',
    images: ['audi-a4-1.jpg', 'audi-a4-2.jpg'],
    isAvailable: true,
    location: 'Luxury Section L-2'
  }
];

// Sample business information
const businessInfo = {
  name: 'AutoMax Concesionario',
  address: '123 Avenida Principal, Ciudad, Estado 12345',
  phone: '(555) 123-4567',
  email: 'info@automax.com',
  website: 'www.automax.com',
  hours: {
    'Lunes': '9:00 AM - 8:00 PM',
    'Martes': '9:00 AM - 8:00 PM',
    'Miércoles': '9:00 AM - 8:00 PM',
    'Jueves': '9:00 AM - 8:00 PM',
    'Viernes': '9:00 AM - 8:00 PM',
    'Sábado': '9:00 AM - 6:00 PM',
    'Domingo': '12:00 PM - 5:00 PM'
  },
  services: [
    'Venta de autos nuevos',
    'Venta de autos usados',
    'Financiamiento y arrendamiento',
    'Evaluación de vehículos usados',
    'Servicio y mantenimiento',
    'Departamento de refacciones',
    'Garantías extendidas',
    'Servicios de seguro'
  ]
};

// Sample available appointment slots
const availableTimeSlots = [
  '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
  '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM'
];

// Sample financing options
const financingOptions = [
  {
    id: 'standard-financing',
    name: 'Préstamo Automotriz Estándar',
    apr: 4.9,
    termMonths: 60,
    description: 'Financiamiento automotriz tradicional con tasas competitivas',
    requirements: ['Buen puntaje crediticio (650+)', 'Comprobante de ingresos', 'Se recomienda enganche']
  },
  {
    id: 'lease-option',
    name: 'Programa de Arrendamiento',
    apr: 2.9,
    termMonths: 36,
    description: 'Pagos mensuales más bajos con opción de arrendamiento',
    requirements: ['Excelente puntaje crediticio (700+)', 'Aplican restricciones de kilometraje']
  },
  {
    id: 'first-time-buyer',
    name: 'Programa de Primer Comprador',
    apr: 6.9,
    termMonths: 72,
    description: 'Programa especial para compradores de primer auto',
    requirements: ['Se acepta historial crediticio limitado', 'Se requiere mayor enganche']
  }
];

module.exports = {
  sampleInventory,
  businessInfo,
  availableTimeSlots,
  financingOptions
};
