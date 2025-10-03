import { useEffect, useRef } from 'react'
import * as LightweightCharts from 'lightweight-charts'
import './TradingChart.css'

function TradingChart({ data, signal, timeframe }) {
  const chartContainerRef = useRef(null)
  const chartRef = useRef(null)
  const candlestickSeriesRef = useRef(null)
  const priceLines = useRef([])

  useEffect(() => {
    if (!chartContainerRef.current || !data || data.length === 0) return

    // Get theme colors
    const rootStyles = getComputedStyle(document.documentElement)
    const textColor = rootStyles.getPropertyValue('--text-secondary').trim() || '#94a3b8'
    const borderColor = rootStyles.getPropertyValue('--border-color').trim() || '#334155'

    // Create chart with v5 API
    const chart = LightweightCharts.createChart(chartContainerRef.current, {
      layout: {
        background: { type: 'solid', color: 'transparent' },
        textColor: textColor,
      },
      grid: {
        vertLines: { color: 'rgba(148, 163, 184, 0.1)' },
        horzLines: { color: 'rgba(148, 163, 184, 0.1)' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: borderColor,
      },
      rightPriceScale: {
        borderColor: borderColor,
      },
    })

    chartRef.current = chart

    // Add candlestick series using v5 API
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderDownColor: '#ef4444',
      borderUpColor: '#10b981',
      wickDownColor: '#ef4444',
      wickUpColor: '#10b981',
    })

    candlestickSeriesRef.current = candlestickSeries

    // Convert data to TradingView format
    const candleData = data.map(d => ({
      time: Math.floor(new Date(d.time).getTime() / 1000),
      open: parseFloat(d.open),
      high: parseFloat(d.high),
      low: parseFloat(d.low),
      close: parseFloat(d.close),
    })).sort((a, b) => a.time - b.time)

    candlestickSeries.setData(candleData)

    // Auto-scale
    chart.timeScale().fitContent()

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      if (chartRef.current) {
        chartRef.current.remove()
      }
    }
  }, [data])

  // Add ICT overlays when signal changes
  useEffect(() => {
    if (!chartRef.current || !candlestickSeriesRef.current || !signal) return

    const series = candlestickSeriesRef.current

    // Clear previous price lines
    priceLines.current.forEach(line => {
      try {
        series.removePriceLine(line)
      } catch (e) {
        // Ignore if already removed
      }
    })
    priceLines.current = []

    // Add current price line
    if (signal.current_price) {
      const currentPriceLine = series.createPriceLine({
        price: signal.current_price,
        color: '#6366f1',
        lineWidth: 2,
        lineStyle: 2, // Dashed
        axisLabelVisible: true,
        title: 'Current',
      })
      priceLines.current.push(currentPriceLine)
    }

    // Add Entry Price
    if (signal.entry_price && signal.signal !== 'HOLD' && signal.signal !== 'SETUP_PENDING') {
      const entryLine = series.createPriceLine({
        price: signal.entry_price,
        color: '#8b5cf6',
        lineWidth: 2,
        lineStyle: 0, // Solid
        axisLabelVisible: true,
        title: `Entry ${signal.signal}`,
      })
      priceLines.current.push(entryLine)
    }

    // Add Stop Loss
    if (signal.stop_loss) {
      const slLine = series.createPriceLine({
        price: signal.stop_loss,
        color: '#ef4444',
        lineWidth: 2,
        lineStyle: 0,
        axisLabelVisible: true,
        title: 'Stop Loss',
      })
      priceLines.current.push(slLine)
    }

    // Add Take Profit levels
    if (signal.take_profit_1) {
      const tp1Line = series.createPriceLine({
        price: signal.take_profit_1,
        color: '#10b981',
        lineWidth: 1,
        lineStyle: 0,
        axisLabelVisible: true,
        title: 'TP1',
      })
      priceLines.current.push(tp1Line)
    }

    if (signal.take_profit_2) {
      const tp2Line = series.createPriceLine({
        price: signal.take_profit_2,
        color: '#10b981',
        lineWidth: 1,
        lineStyle: 0,
        axisLabelVisible: true,
        title: 'TP2',
      })
      priceLines.current.push(tp2Line)
    }

    if (signal.take_profit_3) {
      const tp3Line = series.createPriceLine({
        price: signal.take_profit_3,
        color: '#10b981',
        lineWidth: 1,
        lineStyle: 0,
        axisLabelVisible: true,
        title: 'TP3',
      })
      priceLines.current.push(tp3Line)
    }

    // Add OTE zones if available
    if (signal.ote_data) {
      if (signal.ote_data.ote_0_62) {
        const ote62Line = series.createPriceLine({
          price: signal.ote_data.ote_0_62,
          color: '#f59e0b',
          lineWidth: 1,
          lineStyle: 2,
          axisLabelVisible: true,
          title: 'OTE 0.62',
        })
        priceLines.current.push(ote62Line)
      }

      if (signal.ote_data.ote_0_705) {
        const ote705Line = series.createPriceLine({
          price: signal.ote_data.ote_0_705,
          color: '#f59e0b',
          lineWidth: 2,
          lineStyle: 2,
          axisLabelVisible: true,
          title: 'OTE 0.705',
        })
        priceLines.current.push(ote705Line)
      }

      if (signal.ote_data.ote_0_79) {
        const ote79Line = series.createPriceLine({
          price: signal.ote_data.ote_0_79,
          color: '#f59e0b',
          lineWidth: 1,
          lineStyle: 2,
          axisLabelVisible: true,
          title: 'OTE 0.79',
        })
        priceLines.current.push(ote79Line)
      }
    }

    // Add limit order levels
    if (signal.limit_orders && signal.limit_orders.length > 0) {
      signal.limit_orders.slice(0, 3).forEach((order, idx) => {
        const limitLine = series.createPriceLine({
          price: order.price,
          color: idx === 0 ? '#8b5cf6' : '#a78bfa',
          lineWidth: idx === 0 ? 2 : 1,
          lineStyle: 2,
          axisLabelVisible: true,
          title: `Limit ${idx + 1}`,
        })
        priceLines.current.push(limitLine)
      })
    }

  }, [signal])

  return (
    <div className="card trading-chart-card">
      <div className="card-header">
        <h2 className="card-title">📊 Price Chart</h2>
        <div className="chart-info">
          <span className="timeframe-badge">{timeframe}</span>
          {signal?.killzone_active && (
            <span className="killzone-indicator">
              ⏰ {signal.killzone_name}
            </span>
          )}
        </div>
      </div>
      <div className="trading-chart-container" ref={chartContainerRef} />
      
      {/* Legend */}
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-dot current-price"></span>
          <span>Current Price</span>
        </div>
        {signal?.entry_price && signal.signal !== 'HOLD' && signal.signal !== 'SETUP_PENDING' && (
          <div className="legend-item">
            <span className="legend-dot entry"></span>
            <span>Entry ({signal.signal})</span>
          </div>
        )}
        {signal?.stop_loss && (
          <div className="legend-item">
            <span className="legend-dot stop-loss"></span>
            <span>Stop Loss</span>
          </div>
        )}
        {signal?.take_profit_1 && (
          <div className="legend-item">
            <span className="legend-dot take-profit"></span>
            <span>Take Profits</span>
          </div>
        )}
        {signal?.ote_data && (
          <div className="legend-item">
            <span className="legend-dot ote"></span>
            <span>OTE Zones</span>
          </div>
        )}
        {signal?.limit_orders && signal.limit_orders.length > 0 && (
          <div className="legend-item">
            <span className="legend-dot limit-order"></span>
            <span>Limit Orders</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default TradingChart
