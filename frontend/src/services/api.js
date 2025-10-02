import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'
const WS_URL = 'ws://localhost:8000/ws'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Fetch trading signal for a symbol
 */
export const fetchSignal = async (symbol, timeframe = '15m') => {
  try {
    const formattedSymbol = symbol.replace('/', '-')
    const response = await api.get(`/api/signals/${formattedSymbol}`, {
      params: { timeframe }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching signal:', error)
    throw error
  }
}

/**
 * Fetch current price for a symbol
 */
export const fetchPrice = async (symbol) => {
  try {
    const formattedSymbol = symbol.replace('/', '-')
    const response = await api.get(`/api/price/${formattedSymbol}`)
    return response.data
  } catch (error) {
    console.error('Error fetching price:', error)
    throw error
  }
}

/**
 * Fetch OHLCV (candlestick) data for charting
 */
export const fetchOHLCV = async (symbol, timeframe = '15m', limit = 100) => {
  try {
    const formattedSymbol = symbol.replace('/', '-')
    const response = await api.get(`/api/ohlcv/${formattedSymbol}`, {
      params: { timeframe, limit }
    })
    return response.data.data
  } catch (error) {
    console.error('Error fetching OHLCV:', error)
    throw error
  }
}

/**
 * Connect to WebSocket for real-time updates with auto-reconnection
 */
export const connectWebSocket = (onMessage, onStatusChange) => {
  let ws = null
  let reconnectTimeout = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 5
  const reconnectDelay = 5000 // 5 seconds

  const connect = () => {
    try {
      ws = new WebSocket(WS_URL)

      ws.onopen = () => {
        console.log('✅ WebSocket connected')
        reconnectAttempts = 0
        if (onStatusChange) onStatusChange(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        if (onStatusChange) onStatusChange(false)
      }

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected')
        if (onStatusChange) onStatusChange(false)
        
        // Auto-reconnect with exponential backoff
        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectAttempts++
          const delay = reconnectDelay * reconnectAttempts
          console.log(`🔄 Reconnecting in ${delay/1000}s... (attempt ${reconnectAttempts}/${maxReconnectAttempts})`)
          
          reconnectTimeout = setTimeout(() => {
            connect()
          }, delay)
        } else {
          console.error('❌ Max reconnection attempts reached. Please refresh the page.')
        }
      }

      return ws
    } catch (error) {
      console.error('Error connecting to WebSocket:', error)
      if (onStatusChange) onStatusChange(false)
      return null
    }
  }

  // Initial connection
  connect()

  // Return cleanup function
  return {
    close: () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
      if (ws) {
        ws.close()
      }
    }
  }
}

export default api


