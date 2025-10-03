import { Target, TrendingUp, TrendingDown } from 'lucide-react'
import './LimitOrders.css'

function LimitOrders({ limitOrders, signal }) {
  if (!limitOrders || limitOrders.length === 0) return null

  const getTypeIcon = (type) => {
    if (type.includes('OTE')) return '🎯'
    if (type.includes('ORDER_BLOCK')) return '🟦'
    if (type.includes('FVG')) return '📈'
    if (type.includes('BREAKER')) return '⚡'
    if (type.includes('EQUILIBRIUM')) return '⚖️'
    return '📍'
  }

  const getConfluenceBadge = (confluence) => {
    if (confluence >= 5) return 'high'
    if (confluence >= 3) return 'medium'
    return 'low'
  }

  return (
    <div className="card limit-orders-card">
      <div className="card-header">
        <h2 className="card-title">
          <Target size={20} />
          Limit Order Suggestions
        </h2>
        <span className="limit-orders-subtitle">
          Best entry levels ranked by ICT confluence
        </span>
      </div>

      <div className="limit-orders-grid">
        {limitOrders.slice(0, 3).map((order, idx) => (
          <div 
            key={idx} 
            className={`limit-order-item ${idx === 0 ? 'best-entry' : ''}`}
          >
            {idx === 0 && <div className="best-badge">⭐ Best Entry</div>}
            
            <div className="limit-order-header">
              <span className="limit-order-type">
                {getTypeIcon(order.type)} {order.type.replace(/_/g, ' ')}
              </span>
              <span className={`confluence-badge confluence-${getConfluenceBadge(order.confluence)}`}>
                {order.confluence} Confluences
              </span>
            </div>

            <div className="limit-order-price">
              <span className="price-label">Entry Price</span>
              <span className="price-value">${order.price.toLocaleString()}</span>
            </div>

            <div className="limit-order-description">
              {order.description}
            </div>

            {order.stop_loss && order.take_profit && (
              <div className="limit-order-levels">
                <div className="level-item stop-loss">
                  <span className="level-label">Stop Loss</span>
                  <span className="level-value">${order.stop_loss.toLocaleString()}</span>
                </div>
                
                <div className="level-item take-profit">
                  <span className="level-label">Take Profits</span>
                  <div className="tp-values">
                    {order.take_profit.slice(0, 3).map((tp, tpIdx) => (
                      <span key={tpIdx} className="tp-value">
                        TP{tpIdx + 1}: ${tp.toLocaleString()}
                      </span>
                    ))}
                  </div>
                </div>

                {order.risk_reward && (
                  <div className="level-item risk-reward">
                    <span className="level-label">R:R Ratio</span>
                    <span className="level-value rr-value">1:{order.risk_reward.toFixed(1)}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="limit-orders-note">
        💡 <strong>Tip:</strong> Place limit orders at these levels for optimal entries. 
        Monitor price action for confirmation before execution.
      </div>
    </div>
  )
}

export default LimitOrders

