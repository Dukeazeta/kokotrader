import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import './PriceChart.css'

function PriceChart({ data, signal, timeframe }) {
  if (!data || data.length === 0) return null

  const formatTimeframe = React.useCallback((tf) => {
    if (!tf) return '15m'
    return tf
  }, [])

  const chartData = React.useMemo(() => {
    return data.map(d => ({
      time: new Date(d.timestamp).toLocaleTimeString(),
      price: d.close
    }))
  }, [data])

  const referenceLines = React.useMemo(() => {
    const lines = []

    if (signal?.entry_price) {
      lines.push(
        <ReferenceLine
          key="entry"
          y={signal.entry_price}
          stroke="var(--accent-primary)"
          strokeDasharray="3 3"
          label={{ value: 'Entry', fill: 'var(--accent-primary)', fontSize: 12 }}
        />
      )
    }

    if (signal?.stop_loss) {
      lines.push(
        <ReferenceLine
          key="sl"
          y={signal.stop_loss}
          stroke="var(--error)"
          strokeDasharray="3 3"
          label={{ value: 'SL', fill: 'var(--error)', fontSize: 12 }}
        />
      )
    }

    if (signal?.take_profit_1) {
      lines.push(
        <ReferenceLine
          key="tp1"
          y={signal.take_profit_1}
          stroke="var(--success)"
          strokeDasharray="3 3"
          label={{ value: 'TP1', fill: 'var(--success)', fontSize: 12 }}
        />
      )
    }

    return lines
  }, [signal])

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-time">{payload[0].payload.time}</p>
          <p className="tooltip-price">${payload[0].value.toLocaleString()}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="card chart-card">
      <div className="card-header">
        <h2 className="card-title">Price Chart</h2>
        <div className="chart-info">
          <span className="chart-symbol">{signal?.symbol || 'Loading...'}</span>
          <span className="chart-timeframe">{formatTimeframe(timeframe)}</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" strokeOpacity={0.3} />
          <XAxis
            dataKey="time"
            stroke="var(--text-secondary)"
            style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}
          />
          <YAxis
            stroke="var(--text-secondary)"
            style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}
            domain={['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip />} />

          {referenceLines}

          <Line
            type="monotone"
            dataKey="price"
            stroke="var(--accent-primary)"
            strokeWidth={2}
            dot={false}
            animationDuration={500}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PriceChart


