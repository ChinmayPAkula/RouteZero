// src/api/routeApi.js
import axios from 'axios';
import mockRoute from '../data/mockRoute';

// Set this to true once the backend endpoint is ready and reachable.
// This is the ONLY line that needs to change to switch from mock to real data.
const USE_MOCK_DATA = true;

// Expected backend contract (to confirm with backend teammate):
// GET /api/optimized-route
// Response shape:
// {
//   route: [
//     { id, name, lat, lng, type: "depot" | "delivery" },
//     ...
//   ]
// }
const API_BASE_URL = 'http://localhost:8000'; // placeholder — update when backend URL is known

export async function fetchOptimizedRoute() {
  if (USE_MOCK_DATA) {
    // Simulates async network behavior so calling code doesn't need
    // to change when we switch to the real request later.
    return Promise.resolve(mockRoute);
  }

  const response = await axios.get(`${API_BASE_URL}/api/optimized-route`);
  return response.data;
}