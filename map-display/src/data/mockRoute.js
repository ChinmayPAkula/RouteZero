// src/data/mockRoute.js

// This mock data simulates what the backend's optimized-route endpoint
// will eventually return. Keeping it in its own file (rather than inline
// in a component) means swapping it for a real API response later is a
// one-line change, not a rewrite.

const mockRoute = {
  route: [
    {
      id: 'depot',
      name: 'Depot',
      lat: 12.9716,
      lng: 77.5946,
      type: 'depot',
    },
    {
      id: 'delivery3',
      name: 'Delivery 3',
      lat: 12.9352,
      lng: 77.6245,
      type: 'delivery',
    },
    {
      id: 'delivery1',
      name: 'Delivery 1',
      lat: 12.9850,
      lng: 77.6100,
      type: 'delivery',
    },
    {
      id: 'delivery4',
      name: 'Delivery 4',
      lat: 13.0030,
      lng: 77.5700,
      type: 'delivery',
    },
    {
      id: 'delivery2',
      name: 'Delivery 2',
      lat: 12.9600,
      lng: 77.5500,
      type: 'delivery',
    },
    {
      id: 'depot',
      name: 'Depot',
      lat: 12.9716,
      lng: 77.5946,
      type: 'depot',
    },
  ],
};

export default mockRoute;