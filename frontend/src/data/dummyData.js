export const dummyResult = {
  normalRoute: {
    distanceKm: 42.6,
    timeMin: 78,
    co2Kg: 9.8,
  },

  optimizedRoute: {
    distanceKm: 36.1,
    timeMin: 61,
    co2Kg: 7.2,
  },

  co2SavedKg: 2.6,

  routeCoordinates: [
    [12.9716, 77.5946],
    [12.9650, 77.6030],
    [12.9510, 77.6120],
    [12.9380, 77.6200],
    [12.9280, 77.6280],
    [12.9141, 77.6411],
  ],
}

export const vehicleOptions = [
  {
    id: 'bike',
    label: 'Two-Wheeler',
    capacityKg: 20,
  },

  {
    id: 'van',
    label: 'Mini Van',
    capacityKg: 500,
  },

  {
    id: 'truck',
    label: 'Truck',
    capacityKg: 2000,
  },
]