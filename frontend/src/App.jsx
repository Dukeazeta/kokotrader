import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import SignalCard from './components/SignalCard'
import PriceChart from './components/PriceChart'
import IndicatorsPanel from './components/IndicatorsPanel'
import SymbolSelector from './components/SymbolSelector'
import ConnectionStatus from './components/ConnectionStatus'
import { fetchSignal, fetchOHLCV, connectWebSocket } from './services/api'
import './App.css'

function App() {
  const [symbol, setSymbol] = useState('BTC/USDT')
  const [timeframe, setTimeframe] = useState('15m')
  const [signal, setSignal] = useState(null)
  const [ohlcvData, setOhlcvData] = useState([])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [wsConnected, setWsConnected] = useState(false)

  // Fetch signal and chart data (memoized to prevent recreating function)
  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [signalData, chartData] = await Promise.all([
        fetchSignal(symbol, timeframe),
        fetchOHLCV(symbol, timeframe, 100)
      ])
      
      setSignal(signalData)
      setOhlcvData(chartData)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }, [symbol, timeframe])

  // Initial load
  useEffect(() => {
    loadData()
  }, [symbol, timeframe])

  // WebSocket connection (only updates signal data, not full refresh)
  useEffect(() => {
    const wsConnection = connectWebSocket(
      // onMessage callback
      (data) => {
        if (data.type === 'signal_update') {
          // Only update signal state, preventing full UI refresh
          setSignal(prevSignal => ({
            ...prevSignal,
            ...data.data
          }))
          setLastUpdate(new Date())
        } else if (data.type === 'connected') {
          setWsConnected(true)
        }
      },
      // onStatusChange callback
      (connected) => {
        setWsConnected(connected)
      }
    )

    return () => {
      if (wsConnection) {
        wsConnection.close()
      }
    }
  }, [])

  // Auto refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      loadData()
    }, 30000)

    return () => clearInterval(interval)
  }, [symbol, timeframe])

  return (
    <div className="app">
      <Header 
        lastUpdate={lastUpdate} 
        wsConnected={wsConnected}
        onRefresh={loadData}
      />
      
      <ConnectionStatus wsConnected={wsConnected} />
      
      <div className="container">
        <SymbolSelector
          symbol={symbol}
          timeframe={timeframe}
          onSymbolChange={setSymbol}
          onTimeframeChange={setTimeframe}
        />

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading signals...</p>
          </div>
        ) : (
          <>
            <div className="main-grid">
              <SignalCard signal={signal} />
              <PriceChart data={ohlcvData} signal={signal} />
            </div>

            {signal && <IndicatorsPanel indicators={signal.indicators} />}
          </>
        )}
      </div>
    </div>
  )
}

export default App


