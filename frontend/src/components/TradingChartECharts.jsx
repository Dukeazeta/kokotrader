import { useMemo } from 'react'
import ReactECharts from 'echarts-for-react'
import './TradingChartECharts.css'

function TradingChartECharts({ data, signal, timeframe }) {
  const option = useMemo(() => {
    if (!data || data.length === 0) return null

    // Convert OHLCV data to ECharts candlestick format
    const candleData = data.map(d => [
      d.open,
      d.close,
      d.low,
      d.high
    ])

    const times = data.map(d => 
      new Date(d.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    )

    // Prepare marker lines for ICT levels
    const markLines = []

    // Current Price
    if (signal?.current_price) {
      markLines.push({
        name: 'Current Price',
        yAxis: signal.current_price,
        lineStyle: { color: '#6366f1', type: 'dashed', width: 2 },
        label: { formatter: 'Current', position: 'end', color: '#6366f1' }
      })
    }

    // Entry Price
    if (signal?.entry_price && signal.signal !== 'HOLD' && signal.signal !== 'SETUP_PENDING') {
      markLines.push({
        name: `Entry ${signal.signal}`,
        yAxis: signal.entry_price,
        lineStyle: { color: '#8b5cf6', type: 'solid', width: 2 },
        label: { formatter: `Entry ${signal.signal}`, position: 'end', color: '#8b5cf6' }
      })
    }

    // Stop Loss
    if (signal?.stop_loss) {
      markLines.push({
        name: 'Stop Loss',
        yAxis: signal.stop_loss,
        lineStyle: { color: '#ef4444', type: 'solid', width: 2 },
        label: { formatter: 'SL', position: 'end', color: '#ef4444' }
      })
    }

    // Take Profits
    if (signal?.take_profit_1) {
      markLines.push({
        name: 'TP1',
        yAxis: signal.take_profit_1,
        lineStyle: { color: '#10b981', type: 'solid', width: 1 },
        label: { formatter: 'TP1', position: 'end', color: '#10b981' }
      })
    }
    if (signal?.take_profit_2) {
      markLines.push({
        name: 'TP2',
        yAxis: signal.take_profit_2,
        lineStyle: { color: '#10b981', type: 'dashed', width: 1 },
        label: { formatter: 'TP2', position: 'end', color: '#10b981' }
      })
    }
    if (signal?.take_profit_3) {
      markLines.push({
        name: 'TP3',
        yAxis: signal.take_profit_3,
        lineStyle: { color: '#10b981', type: 'dotted', width: 1 },
        label: { formatter: 'TP3', position: 'end', color: '#10b981' }
      })
    }

    // OTE Zones
    if (signal?.ote_data?.ote_0_62) {
      markLines.push({
        name: 'OTE 0.62',
        yAxis: signal.ote_data.ote_0_62,
        lineStyle: { color: '#f59e0b', type: 'dashed', width: 1 },
        label: { formatter: 'OTE 0.62', position: 'start', color: '#f59e0b' }
      })
    }
    if (signal?.ote_data?.ote_0_705) {
      markLines.push({
        name: 'OTE 0.705',
        yAxis: signal.ote_data.ote_0_705,
        lineStyle: { color: '#f59e0b', type: 'dashed', width: 2 },
        label: { formatter: 'OTE 0.705 (Golden)', position: 'start', color: '#f59e0b' }
      })
    }
    if (signal?.ote_data?.ote_0_79) {
      markLines.push({
        name: 'OTE 0.79',
        yAxis: signal.ote_data.ote_0_79,
        lineStyle: { color: '#f59e0b', type: 'dashed', width: 1 },
        label: { formatter: 'OTE 0.79', position: 'start', color: '#f59e0b' }
      })
    }

    // Limit Orders
    if (signal?.limit_orders) {
      signal.limit_orders.slice(0, 3).forEach((order, idx) => {
        markLines.push({
          name: `Limit ${idx + 1}`,
          yAxis: order.price,
          lineStyle: { 
            color: idx === 0 ? '#8b5cf6' : '#a78bfa', 
            type: 'dashed', 
            width: idx === 0 ? 2 : 1 
          },
          label: { 
            formatter: `Limit ${idx + 1} (${order.confluence})`, 
            position: 'end', 
            color: idx === 0 ? '#8b5cf6' : '#a78bfa' 
          }
        })
      })
    }

    // Get theme colors
    const isDark = document.documentElement.classList.contains('dark') || 
                   window.matchMedia('(prefers-color-scheme: dark)').matches
    
    const textColor = isDark ? '#94a3b8' : '#64748b'
    const gridColor = isDark ? 'rgba(148, 163, 184, 0.1)' : 'rgba(100, 116, 139, 0.1)'

    return {
      backgroundColor: 'transparent',
      grid: {
        left: '3%',
        right: '10%',
        bottom: '10%',
        top: '5%',
        containLabel: true
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        backgroundColor: isDark ? '#1e293b' : '#ffffff',
        borderColor: isDark ? '#334155' : '#e2e8f0',
        textStyle: {
          color: textColor
        },
        formatter: function (params) {
          const data = params[0]
          if (!data) return ''
          const ohlc = data.data
          return `
            <div style="font-size: 12px;">
              <div style="font-weight: bold; margin-bottom: 4px;">${data.name}</div>
              <div>Open: <span style="color: #6366f1;">$${ohlc[0].toLocaleString()}</span></div>
              <div>Close: <span style="color: #6366f1;">$${ohlc[1].toLocaleString()}</span></div>
              <div>Low: <span style="color: #ef4444;">$${ohlc[2].toLocaleString()}</span></div>
              <div>High: <span style="color: #10b981;">$${ohlc[3].toLocaleString()}</span></div>
            </div>
          `
        }
      },
      xAxis: {
        type: 'category',
        data: times,
        axisLine: { lineStyle: { color: textColor } },
        axisLabel: {
          color: textColor,
          fontSize: 11,
          fontFamily: 'monospace'
        },
        splitLine: {
          show: true,
          lineStyle: { color: gridColor }
        }
      },
      yAxis: {
        type: 'value',
        scale: true,
        axisLine: { lineStyle: { color: textColor } },
        axisLabel: {
          color: textColor,
          fontSize: 11,
          fontFamily: 'monospace',
          formatter: (value) => `$${value.toLocaleString()}`
        },
        splitLine: {
          lineStyle: { color: gridColor }
        }
      },
      series: [
        {
          name: 'Price',
          type: 'candlestick',
          data: candleData,
          itemStyle: {
            color: '#10b981',  // Bullish candle
            color0: '#ef4444', // Bearish candle
            borderColor: '#10b981',
            borderColor0: '#ef4444'
          },
          markLine: {
            symbol: 'none',
            data: markLines,
            animation: false
          }
        }
      ]
    }
  }, [data, signal])

  if (!option) {
    return (
      <div className="card echarts-card">
        <div className="card-header">
          <h2 className="card-title">📊 Candlestick Chart</h2>
        </div>
        <div className="chart-empty">No data available</div>
      </div>
    )
  }

  return (
    <div className="card echarts-card">
      <div className="card-header">
        <h2 className="card-title">📊 Candlestick Chart with ICT Levels</h2>
        <div className="chart-info">
          <span className="timeframe-badge">{timeframe}</span>
          {signal?.killzone_active && (
            <span className="killzone-indicator">
              ⏰ {signal.killzone_name}
            </span>
          )}
        </div>
      </div>

      <ReactECharts 
        option={option} 
        style={{ height: '500px', width: '100%' }}
        notMerge={true}
        lazyUpdate={true}
        theme="custom"
      />

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
            <span>Take Profits (3)</span>
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
            <span>Limit Orders ({signal.limit_orders.length})</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default TradingChartECharts

