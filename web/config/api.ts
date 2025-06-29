// API Configuration
export const API_CONFIG = {
  // Fly.io backend URL
  BASE_URL: 'https://chat-app-twilight-snow-4634.fly.dev',
  
  // API endpoints
  ENDPOINTS: {
    CHAT: '/api/chat',
    HEALTH: '/health',
  },
  
  // Headers
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  },
} as const

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`
}

// Helper function to make API calls
export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = getApiUrl(endpoint)
  const response = await fetch(url, {
    headers: {
      ...API_CONFIG.DEFAULT_HEADERS,
      ...options.headers,
    },
    ...options,
  })
  
  if (!response.ok) {
    throw new Error(`API call failed: ${response.status} ${response.statusText}`)
  }
  
  return response.json()
} 