import { useState, useEffect, useCallback } from 'react'
import Header from './components/Header'
import SignalCard from './components/SignalCard'
import PriceChart from './components/PriceChart'
import IndicatorsPanel from './components/IndicatorsPanel'
import SymbolSelector from './components/SymbolSelector'
import ConnectionStatus from './components/ConnectionStatus'
import MTFAnalysis from './components/MTFAnalysis'
import Settings from './components/Settings'
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
  const [userSettings, setUserSettings] = useState(null)

  // Fetch signal and chart data (memoized to prevent recreating function)
  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const strategy = userSettings?.strategy || 'TECHNICAL'
      const [signalData, chartData] = await Promise.all([
        fetchSignal(symbol, timeframe, strategy),
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
  }, [symbol, timeframe, userSettings])

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
      },
      { symbol, timeframe, strategy: (userSettings?.strategy || 'TECHNICAL') }
    )

    return () => {
      if (wsConnection) {
        wsConnection.close()
      }
    }
  }, [symbol, timeframe, userSettings])

  // Auto refresh with configurable interval
  useEffect(() => {
    const refreshInterval = (userSettings?.autoRefreshInterval || 30) * 1000
    const interval = setInterval(() => {
      loadData()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [loadData, userSettings])

  // Handle settings changes
  const handleSettingsChange = (newSettings) => {
    setUserSettings(newSettings)
    localStorage.setItem('kokotrader_settings', JSON.stringify(newSettings))
    // Immediately reload data when critical settings change (e.g., strategy)
    loadData()
  }

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('kokotrader_settings')
    if (savedSettings) {
      try {
        setUserSettings(JSON.parse(savedSettings))
      } catch (e) {
        console.error('Error loading settings:', e)
      }
    }
  }, [])

  const showBanner = !wsConnected

  return (
    <div className={`app${showBanner ? ' app--has-banner' : ''}`}>
      <Header 
        lastUpdate={lastUpdate} 
        wsConnected={wsConnected}
        onRefresh={loadData}
      >
        <Settings onSettingsChange={handleSettingsChange} />
      </Header>
      
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
              <PriceChart data={ohlcvData} signal={signal} timeframe={timeframe} />
            </div>

            {/* Multi-Timeframe Analysis */}
            {signal?.mtf_analysis && userSettings?.enableMTF !== false && (
              <MTFAnalysis mtfData={signal.mtf_analysis} />
            )}

            {signal && <IndicatorsPanel indicators={signal.indicators} />}
          </>
        )}
      </div>
    </div>
  )
}

export default App


