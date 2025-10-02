import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import './PriceChart.css'

function PriceChart({ data, signal }) {
  if (!data || data.length === 0) return null

  const chartData = data.map(d => ({
    time: new Date(d.timestamp).toLocaleTimeString(),
    price: d.close
  }))

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
        {signal && (
          <div className="chart-info">
            <span className="chart-symbol">{signal.symbol}</span>
            <span className="chart-timeframe">{signal.timeframe}</span>
          </div>
        )}
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
          <XAxis 
            dataKey="time" 
            stroke="#94a3b8"
            style={{ fontSize: '0.75rem' }}
          />
          <YAxis 
            stroke="#94a3b8"
            style={{ fontSize: '0.75rem' }}
            domain={['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {signal && signal.entry_price && (
            <ReferenceLine 
              y={signal.entry_price} 
              stroke="#6366f1" 
              strokeDasharray="3 3"
              label={{ value: 'Entry', fill: '#6366f1', fontSize: 12 }}
            />
          )}
          
          {signal && signal.stop_loss && (
            <ReferenceLine 
              y={signal.stop_loss} 
              stroke="#f87171" 
              strokeDasharray="3 3"
              label={{ value: 'SL', fill: '#f87171', fontSize: 12 }}
            />
          )}
          
          {signal && signal.take_profit_1 && (
            <ReferenceLine 
              y={signal.take_profit_1} 
              stroke="#4ade80" 
              strokeDasharray="3 3"
              label={{ value: 'TP1', fill: '#4ade80', fontSize: 12 }}
            />
          )}
          
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#6366f1" 
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


