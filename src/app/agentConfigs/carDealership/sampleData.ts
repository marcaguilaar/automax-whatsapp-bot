// Sample data for the car dealership
export interface Car {
  id: string;
  brand: string;
  model: string;
  year: number;
  price: number;
  color: string;
  mileage: number;
  fuelType: 'gasoline' | 'diesel' | 'hybrid' | 'electric';
  bodyStyle: 'sedan' | 'suv' | 'hatchback' | 'coupe' | 'wagon' | 'pickup';
  transmission: 'manual' | 'automatic';
  engineSize: string;
  fuelEfficiency: string; // mpg or km/l
  features: string[];
  description: string;
  images: string[];
  isAvailable: boolean;
  location: string; // lot location
}

export interface Appointment {
  id: string;
  date: string;
  time: string;
  type: 'test_drive' | 'consultation' | 'inspection' | 'delivery';
  customerName: string;
  customerPhone: string;
  customerEmail?: string;
  carId?: string;
  notes?: string;
  status: 'scheduled' | 'confirmed' | 'cancelled' | 'completed';
}

export interface BusinessInfo {
  name: string;
  address: string;
  phone: string;
  email: string;
  hours: Record<string, string>;
  services: string[];
  website: string;
}

// Sample car inventory
export const sampleInventory: Car[] = [
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
export const businessInfo: BusinessInfo = {
  name: 'Premier Auto Dealership',
  address: '123 Main Street, Cityville, ST 12345',
  phone: '(555) 123-4567',
  email: 'info@premierauto.com',
  website: 'www.premierauto.com',
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
    'Trade-in evaluations',
    'Service and maintenance',
    'Parts department',
    'Extended warranties',
    'Insurance services'
  ]
};

// Sample available appointment slots
export const availableTimeSlots = [
  '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
  '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM'
];

// Sample financing options
export interface FinancingOption {
  id: string;
  name: string;
  apr: number;
  termMonths: number;
  description: string;
  requirements: string[];
}

export const financingOptions: FinancingOption[] = [
  {
    id: 'standard-financing',
    name: 'Standard Auto Loan',
    apr: 4.9,
    termMonths: 60,
    description: 'Traditional auto financing with competitive rates',
    requirements: ['Good credit score (650+)', 'Proof of income', 'Down payment recommended']
  },
  {
    id: 'lease-option',
    name: 'Lease Program',
    apr: 2.9,
    termMonths: 36,
    description: 'Lower monthly payments with lease option',
    requirements: ['Excellent credit score (700+)', 'Mileage restrictions apply']
  },
  {
    id: 'first-time-buyer',
    name: 'First-Time Buyer Program',
    apr: 6.9,
    termMonths: 72,
    description: 'Special program for first-time car buyers',
    requirements: ['Limited credit history accepted', 'Larger down payment required']
  }
];
