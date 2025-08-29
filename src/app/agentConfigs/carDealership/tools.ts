import { tool } from '@openai/agents/realtime';
import { sampleInventory, businessInfo, availableTimeSlots, financingOptions } from './sampleData';
import type { Car, Appointment, FinancingOption } from './sampleData';

// Simulated database for appointments
let appointments: Appointment[] = [];
let appointmentCounter = 1;

// Tool for searching car inventory
export const searchInventory = tool({
  name: 'searchInventory',
  description: 'Search for cars in the dealership inventory based on various criteria. The LLM can flexibly interpret user needs and apply appropriate filters.',
  parameters: {
    type: 'object',
    properties: {
      brand: {
        type: 'string',
        description: 'Car brand (e.g., BMW, Toyota, Tesla, Ford, Honda, Audi)'
      },
      model: {
        type: 'string',
        description: 'Specific car model'
      },
      priceMin: {
        type: 'number',
        description: 'Minimum price range'
      },
      priceMax: {
        type: 'number',
        description: 'Maximum price range'
      },
      year: {
        type: 'number',
        description: 'Specific year or minimum year'
      },
      fuelType: {
        type: 'string',
        enum: ['gasoline', 'diesel', 'hybrid', 'electric'],
        description: 'Type of fuel/power source'
      },
      bodyStyle: {
        type: 'string',
        enum: ['sedan', 'suv', 'hatchback', 'coupe', 'wagon', 'pickup'],
        description: 'Vehicle body style'
      },
      transmission: {
        type: 'string',
        enum: ['manual', 'automatic'],
        description: 'Transmission type'
      },
      maxMileage: {
        type: 'number',
        description: 'Maximum acceptable mileage'
      },
      usage: {
        type: 'string',
        description: 'Intended use (e.g., "commuting", "family", "work", "luxury", "sport")'
      },
      budget: {
        type: 'string',
        description: 'Budget category (e.g., "economico", "mid-range", "luxury")'
      },
      priorities: {
        type: 'array',
        items: { type: 'string' },
        description: 'Customer priorities (e.g., "fuel efficiency", "reliability", "luxury", "performance")'
      }
    }
  },
  execute: async (params: any) => {
    let results = [...sampleInventory];

    // Apply filters based on parameters
    if (params.brand) {
      results = results.filter(car => 
        car.brand.toLowerCase().includes(params.brand.toLowerCase())
      );
    }

    if (params.model) {
      results = results.filter(car => 
        car.model.toLowerCase().includes(params.model.toLowerCase())
      );
    }

    if (params.priceMin) {
      results = results.filter(car => car.price >= params.priceMin);
    }

    if (params.priceMax) {
      results = results.filter(car => car.price <= params.priceMax);
    }

    if (params.year) {
      results = results.filter(car => car.year >= params.year);
    }

    if (params.fuelType) {
      results = results.filter(car => car.fuelType === params.fuelType);
    }

    if (params.bodyStyle) {
      results = results.filter(car => car.bodyStyle === params.bodyStyle);
    }

    if (params.transmission) {
      results = results.filter(car => car.transmission === params.transmission);
    }

    if (params.maxMileage) {
      results = results.filter(car => car.mileage <= params.maxMileage);
    }

    // Smart filtering based on usage and budget
    if (params.usage) {
      const usage = params.usage.toLowerCase();
      if (usage.includes('commut') || usage.includes('work')) {
        // Prioritize fuel efficient cars for commuting
        results = results.sort((a, b) => {
          const aEfficient = a.fuelType === 'electric' || a.fuelType === 'hybrid' || 
                           a.fuelEfficiency.includes('3') || a.fuelEfficiency.includes('4');
          const bEfficient = b.fuelType === 'electric' || b.fuelType === 'hybrid' || 
                           b.fuelEfficiency.includes('3') || b.fuelEfficiency.includes('4');
          return bEfficient ? 1 : -1;
        });
      } else if (usage.includes('family')) {
        // Prioritize SUVs and larger vehicles for families
        results = results.filter(car => 
          car.bodyStyle === 'suv' || car.bodyStyle === 'wagon' || car.bodyStyle === 'pickup'
        );
      } else if (usage.includes('luxury')) {
        results = results.filter(car => 
          car.brand === 'BMW' || car.brand === 'Audi' || car.price > 40000
        );
      }
    }

    if (params.budget) {
      const budget = params.budget.toLowerCase();
      if (budget.includes('econom') || budget.includes('cheap') || budget.includes('affordable')) {
        results = results.filter(car => car.price < 30000);
      } else if (budget.includes('luxury') || budget.includes('premium')) {
        results = results.filter(car => car.price > 40000);
      } else if (budget.includes('mid')) {
        results = results.filter(car => car.price >= 25000 && car.price <= 45000);
      }
    }

    // Filter only available cars
    results = results.filter(car => car.isAvailable);

    // Return formatted results
    return {
      success: true,
      totalFound: results.length,
      cars: results.map(car => ({
        id: car.id,
        brand: car.brand,
        model: car.model,
        year: car.year,
        price: car.price,
        color: car.color,
        mileage: car.mileage,
        fuelType: car.fuelType,
        bodyStyle: car.bodyStyle,
        transmission: car.transmission,
        fuelEfficiency: car.fuelEfficiency,
        keyFeatures: car.features.slice(0, 3), // Show only top 3 features
        description: car.description,
        location: car.location
      }))
    };
  }
});

// Tool for getting detailed information about a specific car
export const getCarDetails = tool({
  name: 'getCarDetails',
  description: 'Get detailed information about a specific car by ID',
  parameters: {
    type: 'object',
    properties: {
      carId: {
        type: 'string',
        description: 'The unique ID of the car',
        required: true
      }
    },
    required: ['carId']
  },
  execute: async (params: any) => {
    const car = sampleInventory.find((c: Car) => c.id === params.carId);
    
    if (!car) {
      return {
        success: false,
        error: 'Car not found with the provided ID'
      };
    }

    if (!car.isAvailable) {
      return {
        success: false,
        error: 'This car is no longer available'
      };
    }

    return {
      success: true,
      car: {
        ...car,
        // Include all details for this specific request
      }
    };
  }
});

// Tool for getting available appointment slots
export const getAvailableAppointmentSlots = tool({
  name: 'getAvailableAppointmentSlots',
  description: 'Get available appointment slots for a specific date and type',
  parameters: {
    type: 'object',
    properties: {
      date: {
        type: 'string',
        description: 'Preferred date in YYYY-MM-DD format'
      },
      appointmentType: {
        type: 'string',
        enum: ['test_drive', 'consultation', 'inspection', 'delivery'],
        description: 'Type of appointment needed'
      }
    }
  },
  execute: async (params: any) => {
    // Simple simulation - in real life, this would check a calendar system
    const bookedSlots = appointments
      .filter(apt => apt.date === params.date && apt.status !== 'cancelled')
      .map(apt => apt.time);

    const availableSlots = availableTimeSlots.filter(slot => 
      !bookedSlots.includes(slot)
    );

    return {
      success: true,
      date: params.date,
      availableSlots: availableSlots,
      appointmentType: params.appointmentType
    };
  }
});

// Tool for scheduling an appointment
export const scheduleAppointment = tool({
  name: 'scheduleAppointment',
  description: 'Schedule an appointment for the customer. Requires customer contact information.',
  parameters: {
    type: 'object',
    properties: {
      date: {
        type: 'string',
        description: 'Appointment date in YYYY-MM-DD format',
        required: true
      },
      time: {
        type: 'string',
        description: 'Appointment time (e.g., "10:00 AM")',
        required: true
      },
      appointmentType: {
        type: 'string',
        enum: ['test_drive', 'consultation', 'inspection', 'delivery'],
        description: 'Type of appointment',
        required: true
      },
      customerName: {
        type: 'string',
        description: 'Customer full name',
        required: true
      },
      customerPhone: {
        type: 'string',
        description: 'Customer phone number',
        required: true
      },
      customerEmail: {
        type: 'string',
        description: 'Customer email address'
      },
      carId: {
        type: 'string',
        description: 'ID of the car if appointment is related to a specific vehicle'
      },
      notes: {
        type: 'string',
        description: 'Additional notes or special requests'
      }
    },
    required: ['date', 'time', 'appointmentType', 'customerName', 'customerPhone']
  },
  execute: async (params: any) => {
    // Check if the slot is available
    const conflictingAppointment = appointments.find(apt => 
      apt.date === params.date && 
      apt.time === params.time && 
      apt.status !== 'cancelled'
    );

    if (conflictingAppointment) {
      return {
        success: false,
        error: 'This time slot is already booked. Please choose a different time.'
      };
    }

    // Create new appointment
    const newAppointment: Appointment = {
      id: `apt-${appointmentCounter++}`,
      date: params.date,
      time: params.time,
      type: params.appointmentType,
      customerName: params.customerName,
      customerPhone: params.customerPhone,
      customerEmail: params.customerEmail,
      carId: params.carId,
      notes: params.notes,
      status: 'scheduled'
    };

    appointments.push(newAppointment);

    return {
      success: true,
      appointment: newAppointment,
      confirmationNumber: newAppointment.id,
      message: `Appointment scheduled successfully! Your confirmation number is ${newAppointment.id}.`
    };
  }
});

// Tool for getting business information
export const getBusinessInfo = tool({
  name: 'getBusinessInfo',
  description: 'Get general business information like hours, location, contact details, and services',
  parameters: {
    type: 'object',
    properties: {
      infoType: {
        type: 'string',
        enum: ['hours', 'location', 'contact', 'services', 'all'],
        description: 'Type of information requested'
      }
    }
  },
  execute: async (params: any) => {
    const { infoType = 'all' } = params;

    let responseData: any = {};

    switch (infoType) {
      case 'hours':
        responseData = { hours: businessInfo.hours };
        break;
      case 'location':
        responseData = { 
          name: businessInfo.name,
          address: businessInfo.address 
        };
        break;
      case 'contact':
        responseData = { 
          phone: businessInfo.phone,
          email: businessInfo.email,
          website: businessInfo.website
        };
        break;
      case 'services':
        responseData = { services: businessInfo.services };
        break;
      default:
        responseData = businessInfo;
    }

    return {
      success: true,
      ...responseData
    };
  }
});

// Tool for getting financing options
export const getFinancingOptions = tool({
  name: 'getFinancingOptions',
  description: 'Get available financing and leasing options',
  parameters: {
    type: 'object',
    properties: {
      carPrice: {
        type: 'number',
        description: 'Price of the car to calculate monthly payments'
      },
      downPayment: {
        type: 'number',
        description: 'Down payment amount'
      },
      creditProfile: {
        type: 'string',
        enum: ['excellent', 'good', 'fair', 'limited'],
        description: 'Customer credit profile'
      }
    }
  },
  execute: async (params: any) => {
    let availableOptions = [...financingOptions];

    // Filter options based on credit profile
    if (params.creditProfile) {
      if (params.creditProfile === 'limited') {
        availableOptions = availableOptions.filter(opt => 
          opt.id === 'first-time-buyer' || opt.id === 'standard-financing'
        );
      } else if (params.creditProfile === 'fair') {
        availableOptions = availableOptions.filter(opt => 
          opt.id !== 'lease-option'
        );
      }
    }

    // Calculate monthly payments if car price is provided
    if (params.carPrice) {
      availableOptions = availableOptions.map(option => {
        const principal = params.carPrice - (params.downPayment || 0);
        const monthlyRate = option.apr / 100 / 12;
        const monthlyPayment = (principal * monthlyRate * Math.pow(1 + monthlyRate, option.termMonths)) / 
                              (Math.pow(1 + monthlyRate, option.termMonths) - 1);

        return {
          ...option,
          estimatedMonthlyPayment: Math.round(monthlyPayment)
        };
      });
    }

    return {
      success: true,
      financingOptions: availableOptions,
      note: 'All rates and terms subject to credit approval. Monthly payments are estimates.'
    };
  }
});

// Export all tools
export const carDealershipTools = [
  searchInventory,
  getCarDetails,
  getAvailableAppointmentSlots,
  scheduleAppointment,
  getBusinessInfo,
  getFinancingOptions
];
