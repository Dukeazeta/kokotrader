import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, ReferenceArea } from 'recharts'
import './AdvancedPriceChart.css'

function AdvancedPriceChart({ data, signal, timeframe }) {
  if (!data || data.length === 0) {
    return (
      <div className="card chart-card">
        <div className="card-header">
          <h2 className="card-title">📊 Price Chart</h2>
        </div>
        <div className="chart-empty">No data available</div>
      </div>
    )
  }

  // Convert OHLCV to simple price data for line chart
  const chartData = data.map(d => ({
    time: new Date(d.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    price: d.close,
    high: d.high,
    low: d.low,
  }))

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="custom-tooltip">
          <p className="tooltip-time">{data.time}</p>
          <p className="tooltip-price">Price: ${data.price?.toLocaleString()}</p>
          <p className="tooltip-high">High: ${data.high?.toLocaleString()}</p>
          <p className="tooltip-low">Low: ${data.low?.toLocaleString()}</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="card advanced-chart-card">
      <div className="card-header">
        <h2 className="card-title">📊 Price Chart with ICT Levels</h2>
        <div className="chart-info">
          <span className="timeframe-badge">{timeframe}</span>
          {signal?.killzone_active && (
            <span className="killzone-indicator">
              ⏰ {signal.killzone_name}
            </span>
          )}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={500}>
        <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
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

          {/* Current Price Line */}
          {signal?.current_price && (
            <ReferenceLine
              y={signal.current_price}
              stroke="#6366f1"
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ value: 'Current', position: 'right', fill: '#6366f1', fontSize: 12 }}
            />
          )}

          {/* Entry Price */}
          {signal?.entry_price && signal.signal !== 'HOLD' && signal.signal !== 'SETUP_PENDING' && (
            <ReferenceLine
              y={signal.entry_price}
              stroke="#8b5cf6"
              strokeWidth={2}
              label={{ value: `Entry ${signal.signal}`, position: 'right', fill: '#8b5cf6', fontSize: 12 }}
            />
          )}

          {/* Stop Loss */}
          {signal?.stop_loss && (
            <ReferenceLine
              y={signal.stop_loss}
              stroke="#ef4444"
              strokeWidth={2}
              label={{ value: 'SL', position: 'right', fill: '#ef4444', fontSize: 12 }}
            />
          )}

          {/* Take Profits */}
          {signal?.take_profit_1 && (
            <ReferenceLine
              y={signal.take_profit_1}
              stroke="#10b981"
              strokeWidth={1}
              label={{ value: 'TP1', position: 'right', fill: '#10b981', fontSize: 11 }}
            />
          )}
          {signal?.take_profit_2 && (
            <ReferenceLine
              y={signal.take_profit_2}
              stroke="#10b981"
              strokeWidth={1}
              strokeDasharray="3 3"
              label={{ value: 'TP2', position: 'right', fill: '#10b981', fontSize: 11 }}
            />
          )}
          {signal?.take_profit_3 && (
            <ReferenceLine
              y={signal.take_profit_3}
              stroke="#10b981"
              strokeWidth={1}
              strokeDasharray="5 5"
              label={{ value: 'TP3', position: 'right', fill: '#10b981', fontSize: 11 }}
            />
          )}

          {/* OTE Zones */}
          {signal?.ote_data?.ote_0_62 && (
            <ReferenceLine
              y={signal.ote_data.ote_0_62}
              stroke="#f59e0b"
              strokeWidth={1}
              strokeDasharray="3 3"
              label={{ value: 'OTE 0.62', position: 'left', fill: '#f59e0b', fontSize: 10 }}
            />
          )}
          {signal?.ote_data?.ote_0_705 && (
            <ReferenceLine
              y={signal.ote_data.ote_0_705}
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="3 3"
              label={{ value: 'OTE 0.705 (Golden)', position: 'left', fill: '#f59e0b', fontSize: 10 }}
            />
          )}
          {signal?.ote_data?.ote_0_79 && (
            <ReferenceLine
              y={signal.ote_data.ote_0_79}
              stroke="#f59e0b"
              strokeWidth={1}
              strokeDasharray="3 3"
              label={{ value: 'OTE 0.79', position: 'left', fill: '#f59e0b', fontSize: 10 }}
            />
          )}

          {/* Limit Orders */}
          {signal?.limit_orders?.map((order, idx) => (
            <ReferenceLine
              key={idx}
              y={order.price}
              stroke={idx === 0 ? '#8b5cf6' : '#a78bfa'}
              strokeWidth={idx === 0 ? 2 : 1}
              strokeDasharray="5 5"
              label={{
                value: `Limit ${idx + 1} (${order.confluence})`,
                position: 'right',
                fill: idx === 0 ? '#8b5cf6' : '#a78bfa',
                fontSize: 10
              }}
            />
          ))}

          {/* OTE Zone Area (if in zone) */}
          {signal?.ote_data?.in_ote_zone && signal.ote_data.ote_0_62 && signal.ote_data.ote_0_79 && (
            <ReferenceArea
              y1={signal.ote_data.ote_0_62}
              y2={signal.ote_data.ote_0_79}
              fill="#f59e0b"
              fillOpacity={0.1}
              label={{ value: 'OTE Zone', position: 'insideTopLeft', fill: '#f59e0b' }}
            />
          )}

          {/* Main Price Line */}
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

export default AdvancedPriceChart

