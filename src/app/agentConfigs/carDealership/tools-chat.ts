import { sampleInventory, businessInfo, availableTimeSlots, financingOptions } from './sampleData';
import type { Car, Appointment, FinancingOption } from './sampleData';

// Simulated database for appointments
let appointments: Appointment[] = [];
let appointmentCounter = 1;

// Tool implementations for Chat Completions API
export const searchInventory = {
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
};

export const getCarDetails = {
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
};

export const getAvailableAppointmentSlots = {
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
};

export const scheduleAppointment = {
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
};

export const getBusinessInfo = {
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
};

export const getFinancingOptions = {
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
};
