import { TrendingUp, TrendingDown, Activity, Target, Shield, Lock, CheckCircle, ArrowRight } from 'lucide-react'
import './SignalCard.css'

function SignalCard({ signal }) {
  if (!signal) return null

  const getSignalIcon = () => {
    switch (signal.signal) {
      case 'LONG':
        return <TrendingUp size={24} />
      case 'SHORT':
        return <TrendingDown size={24} />
      default:
        return <Activity size={24} />
    }
  }

  const getSignalClass = () => {
    return `badge badge-${signal.signal.toLowerCase()}`
  }

  const getStrengthClass = () => {
    return `badge badge-${signal.strength.toLowerCase()}`
  }

  const getStabilityIcon = () => {
    if (signal.signal_stability?.includes('✅')) {
      return <CheckCircle size={16} className="stability-icon-confirmed" />
    }
    return <Lock size={16} className="stability-icon-locked" />
  }

  return (
    <div className="card signal-card">
      <div className="card-header">
        <h2 className="card-title">Trading Signal</h2>
        <div className="signal-header-right">
          {signal.strategy_used && (
            <span className={`strategy-badge strategy-${signal.strategy_used.toLowerCase()}`}>
              {signal.strategy_used === 'SMC' ? '🎯 SMC' : '📊 Tech'}
            </span>
          )}
          <div className="signal-icon">
            {getSignalIcon()}
          </div>
        </div>
      </div>

      {/* Signal Stability Status */}
      {signal.signal_stability && (
        <div className={`signal-stability ${signal.signal_stability.includes('✅') ? 'stability-confirmed' : 'stability-locked'}`}>
          {getStabilityIcon()}
          <span className="stability-text">{signal.signal_stability}</span>
        </div>
      )}

      {/* Previous Signal Comparison */}
      {signal.previous_signal && signal.previous_signal !== signal.signal && (
        <div className="signal-change">
          <span className="signal-change-label">Signal Changed:</span>
          <div className="signal-change-flow">
            <span className={`badge badge-${signal.previous_signal.toLowerCase()}`}>
              {signal.previous_signal}
            </span>
            <ArrowRight size={16} className="change-arrow" />
            <span className={getSignalClass()}>
              {signal.signal}
            </span>
          </div>
        </div>
      )}

      <div className="signal-main">
        <div className="signal-badges">
          <span className={getSignalClass()}>
            {signal.signal}
          </span>
          <span className={getStrengthClass()}>
            {signal.strength}
          </span>
        </div>

        <div className="confidence-meter">
          <div className="confidence-label">
            <span>Confidence</span>
            <span className="confidence-value">{signal.confidence}%</span>
          </div>
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${signal.confidence}%`,
                background: signal.confidence > 75 ? 'var(--success)' : signal.confidence > 50 ? 'var(--warning)' : 'var(--error)'
              }}
            />
          </div>
        </div>

        <div className="price-info">
          <div className="info-item">
            <span className="info-label">Current Price</span>
            <span className="info-value price">${signal.current_price.toLocaleString()}</span>
          </div>
          
          {signal.entry_price && (
            <div className="info-item">
              <span className="info-label">Entry Price</span>
              <span className="info-value">${signal.entry_price.toLocaleString()}</span>
            </div>
          )}
        </div>

        {signal.signal !== 'HOLD' && (
          <>
            <div className="levels-section">
              <div className="level-header">
                <Shield size={16} />
                <span>Stop Loss</span>
              </div>
              <div className="level-value stop-loss">
                ${signal.stop_loss?.toLocaleString()}
              </div>
            </div>

            <div className="levels-section">
              <div className="level-header">
                <Target size={16} />
                <span>Take Profit Levels</span>
              </div>
              <div className="tp-levels">
                <div className="tp-item">
                  <span>TP1</span>
                  <span>${signal.take_profit_1?.toLocaleString()}</span>
                </div>
                <div className="tp-item">
                  <span>TP2</span>
                  <span>${signal.take_profit_2?.toLocaleString()}</span>
                </div>
                <div className="tp-item">
                  <span>TP3</span>
                  <span>${signal.take_profit_3?.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <div className="risk-info">
              <div className="info-item">
                <span className="info-label">Risk/Reward</span>
                <span className="info-value">1:{signal.risk_reward_ratio}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Position Size</span>
                <span className="info-value small">{signal.position_size_suggestion}</span>
              </div>
            </div>
          </>
        )}

        <div className="market-context">
          <div className="context-item">
            <span>Trend:</span>
            <span className={`trend-${signal.trend.toLowerCase()}`}>{signal.trend}</span>
          </div>
          <div className="context-item">
            <span>Volatility:</span>
            <span>{signal.volatility}</span>
          </div>
        </div>

        <div className="confluences">
          <h3>Confluences</h3>
          <ul>
            {signal.confluences.map((conf, idx) => (
              <li key={idx}>{conf}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default SignalCard


