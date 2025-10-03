import './IndicatorsPanel.css'

function IndicatorsPanel({ indicators }) {
  if (!indicators) return null

  const formatNumber = (num) => {
    if (num === undefined || num === null) return 'N/A'
    return typeof num === 'number' ? num.toFixed(2) : num
  }

  const getRSIColor = (rsi) => {
    if (rsi < 30) return 'var(--success)'
    if (rsi > 70) return 'var(--error)'
    return 'var(--warning)'
  }

  const getADXStrength = (adx) => {
    if (adx > 50) return 'Very Strong'
    if (adx > 25) return 'Strong'
    if (adx > 20) return 'Moderate'
    return 'Weak'
  }

  return (
    <div className="card indicators-panel">
      <div className="card-header">
        <h2 className="card-title">Technical Indicators</h2>
      </div>

      <div className="indicators-grid">
        {/* RSI */}
        <div className="indicator-card">
          <div className="indicator-header">
            <span className="indicator-name">RSI (14)</span>
            <span 
              className="indicator-value"
              style={{ color: getRSIColor(indicators.rsi) }}
            >
              {formatNumber(indicators.rsi)}
            </span>
          </div>
          <div className="indicator-bar">
            <div 
              className="indicator-fill"
              style={{ 
                width: `${indicators.rsi}%`,
                background: getRSIColor(indicators.rsi)
              }}
            />
          </div>
          <div className="indicator-labels">
            <span>Oversold (30)</span>
            <span>Overbought (70)</span>
          </div>
        </div>

        {/* MACD */}
        <div className="indicator-card">
          <div className="indicator-header">
            <span className="indicator-name">MACD</span>
            <span className="indicator-value">{formatNumber(indicators.macd)}</span>
          </div>
          <div className="indicator-details">
            <div className="detail-row">
              <span>Signal:</span>
              <span>{formatNumber(indicators.macd_signal)}</span>
            </div>
            <div className="detail-row">
              <span>Histogram:</span>
              <span style={{ color: indicators.macd_diff > 0 ? 'var(--success)' : 'var(--error)' }}>
                {formatNumber(indicators.macd_diff)}
              </span>
            </div>
          </div>
        </div>

        {/* ADX */}
        <div className="indicator-card">
          <div className="indicator-header">
            <span className="indicator-name">ADX (Trend Strength)</span>
            <span className="indicator-value">{formatNumber(indicators.adx)}</span>
          </div>
          <div className="trend-strength">
            {getADXStrength(indicators.adx)}
          </div>
          <div className="indicator-details">
            <div className="detail-row">
              <span>+DI:</span>
              <span style={{ color: 'var(--success)' }}>{formatNumber(indicators.adx_pos)}</span>
            </div>
            <div className="detail-row">
              <span>-DI:</span>
              <span style={{ color: 'var(--error)' }}>{formatNumber(indicators.adx_neg)}</span>
            </div>
          </div>
        </div>

        {/* EMAs */}
        <div className="indicator-card">
          <div className="indicator-header">
            <span className="indicator-name">Moving Averages</span>
          </div>
          <div className="indicator-details">
            <div className="detail-row">
              <span>EMA 9:</span>
              <span>{formatNumber(indicators.ema_9)}</span>
            </div>
            <div className="detail-row">
              <span>EMA 21:</span>
              <span>{formatNumber(indicators.ema_21)}</span>
            </div>
            <div className="detail-row">
              <span>EMA 50:</span>
              <span>{formatNumber(indicators.ema_50)}</span>
            </div>
            {indicators.ema_200 && (
              <div className="detail-row">
                <span>EMA 200:</span>
                <span>{formatNumber(indicators.ema_200)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Bollinger Bands */}
        <div className="indicator-card">
          <div className="indicator-header">
            <span className="indicator-name">Bollinger Bands</span>
          </div>
          <div className="indicator-details">
            <div className="detail-row">
              <span>Upper:</span>
              <span>{formatNumber(indicators.bb_upper)}</span>
            </div>
            <div className="detail-row">
              <span>Middle:</span>
              <span>{formatNumber(indicators.bb_middle)}</span>
            </div>
            <div className="detail-row">
              <span>Lower:</span>
              <span>{formatNumber(indicators.bb_lower)}</span>
            </div>
            <div className="detail-row">
              <span>Width:</span>
              <span>{formatNumber(indicators.bb_width)}</span>
            </div>
          </div>
        </div>

        {/* Stochastic */}
        <div className="indicator-card">
          <div className="indicator-header">
            <span className="indicator-name">Stochastic</span>
          </div>
          <div className="indicator-details">
            <div className="detail-row">
              <span>%K:</span>
              <span style={{ 
                color: indicators.stoch_k < 20 ? 'var(--success)' : indicators.stoch_k > 80 ? 'var(--error)' : 'var(--warning)'
              }}>
                {formatNumber(indicators.stoch_k)}
              </span>
            </div>
            <div className="detail-row">
              <span>%D:</span>
              <span>{formatNumber(indicators.stoch_d)}</span>
            </div>
          </div>
        </div>

        {/* ATR */}
        <div className="indicator-card">
          <div className="indicator-header">
            <span className="indicator-name">ATR (Volatility)</span>
            <span className="indicator-value">{formatNumber(indicators.atr)}</span>
          </div>
        </div>

        {/* Volume */}
        <div className="indicator-card">
          <div className="indicator-header">
            <span className="indicator-name">Volume Analysis</span>
          </div>
          <div className="indicator-details">
            <div className="detail-row">
              <span>Current:</span>
              <span>{formatNumber(indicators.volume)}</span>
            </div>
            <div className="detail-row">
              <span>Avg (20):</span>
              <span>{formatNumber(indicators.avg_volume_20)}</span>
            </div>
            <div className="detail-row">
              <span>Ratio:</span>
              <span style={{ 
                color: indicators.volume_ratio > 1.5 ? 'var(--success)' : 'var(--warning)' 
              }}>
                {formatNumber(indicators.volume_ratio)}x
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default IndicatorsPanel


