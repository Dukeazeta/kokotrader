import { TrendingUp, TrendingDown, Activity, Target, Shield, Lock, CheckCircle, ArrowRight, Clock, Zap } from 'lucide-react'
import './SignalCard.css'

function SignalCard({ signal }) {
  if (!signal) return null

  const isPending = signal.signal === 'SETUP_PENDING'
  const isAwaiting = signal.signal === 'AWAITING_CONFIRMATION'
  const isActive = !isPending && !isAwaiting

  const getSignalIcon = () => {
    if (isPending) return <Clock size={24} />
    if (isAwaiting) return <Activity size={24} />
    
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
    if (isPending) return 'badge badge-hold'
    if (isAwaiting) return 'badge badge-hold'
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
        <h2 className="card-title">
          {isPending ? '⏸️ Setup Pending' : isAwaiting ? '⏳ Awaiting Confirmation' : '🎯 ICT Signal'}
        </h2>
        <div className="signal-header-right">
          {signal.killzone_active && (
            <span className="killzone-badge">
              ⏰ {signal.killzone_name}
            </span>
          )}
          {signal.leverage_suggestion && isActive && (
            <span className={`leverage-badge leverage-${signal.leverage_suggestion.risk_level.toLowerCase()}`}>
              {signal.leverage_suggestion.suggested_leverage}x
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
        {/* Pending Levels Display */}
        {(isPending || isAwaiting) && signal.pending_levels && signal.pending_levels.length > 0 && (
          <div className="pending-levels-section">
            <h3 className="pending-levels-title">
              {isPending ? '📍 Nearby Key Levels' : '🎯 Price at Key Level'}
            </h3>
            {signal.pending_levels.slice(0, 3).map((level, idx) => (
              <div key={idx} className="pending-level-item">
                <span className="level-type">{level.type?.replace(/_/g, ' ')}</span>
                <span className="level-price">${level.price?.toLocaleString()}</span>
                {level.confluence && (
                  <span className="level-confluence">{level.confluence} confluences</span>
                )}
              </div>
            ))}
            <p className="pending-note">
              {isPending ? '💡 Waiting for price to reach one of these levels' : '⏳ Waiting for confirmation candle'}
            </p>
          </div>
        )}

        <div className="signal-badges">
          <span className={getSignalClass()}>
            {isPending ? 'PENDING' : isAwaiting ? 'AWAITING' : signal.signal}
          </span>
          <span className={getStrengthClass()}>
            {signal.strength}
          </span>
        </div>

        {/* Leverage Suggestion Display */}
        {signal.leverage_suggestion && isActive && (
          <div className="leverage-section">
            <div className="leverage-header">
              <Zap size={16} />
              <span className="leverage-title">Leverage Suggestion</span>
            </div>
            <div className="leverage-details">
              <div className="leverage-main">
                <span className="leverage-multiplier">{signal.leverage_suggestion.suggested_leverage}x</span>
                <span className={`leverage-risk leverage-risk-${signal.leverage_suggestion.risk_level.toLowerCase()}`}>
                  {signal.leverage_suggestion.risk_level} RISK
                </span>
              </div>
              <div className="leverage-positions">
                <div className="position-item">
                  <span className="position-label">1% Account Risk:</span>
                  <span className="position-value">{signal.leverage_suggestion.position_size_1pct_risk}</span>
                </div>
                <div className="position-item">
                  <span className="position-label">2% Account Risk:</span>
                  <span className="position-value">{signal.leverage_suggestion.position_size_2pct_risk}</span>
                </div>
              </div>
              <div className="leverage-warning">
                ⚠️ Liquidation at {signal.leverage_suggestion.liquidation_distance} from entry
              </div>
              <div className="leverage-recommendation">
                {signal.leverage_suggestion.recommendation}
              </div>
            </div>
          </div>
        )}

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

        {/* OTE Zones Display */}
        {signal.ote_data && Object.keys(signal.ote_data).length > 0 && (
          <div className="ote-zones-section">
            <h3 className="ote-title">🎯 Optimal Trade Entry (OTE) Zones</h3>
            <div className="ote-levels">
              {signal.ote_data.ote_0_62 && (
                <div className="ote-level">
                  <span className="ote-label">0.62 Fib</span>
                  <span className="ote-value">${signal.ote_data.ote_0_62.toLocaleString()}</span>
                </div>
              )}
              {signal.ote_data.ote_0_705 && (
                <div className="ote-level golden">
                  <span className="ote-label">0.705 Fib (Golden Pocket)</span>
                  <span className="ote-value">${signal.ote_data.ote_0_705.toLocaleString()}</span>
                </div>
              )}
              {signal.ote_data.ote_0_79 && (
                <div className="ote-level">
                  <span className="ote-label">0.79 Fib</span>
                  <span className="ote-value">${signal.ote_data.ote_0_79.toLocaleString()}</span>
                </div>
              )}
            </div>
            {signal.ote_data.in_ote_zone && (
              <div className="ote-active">
                ✅ Price in OTE zone - {signal.ote_data.direction} setup
              </div>
            )}
          </div>
        )}

        <div className="confluences">
          <h3>ICT Confluences</h3>
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


