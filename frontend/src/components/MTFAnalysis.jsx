import { TrendingUp, TrendingDown, Minus, CheckCircle, AlertTriangle } from 'lucide-react'
import './MTFAnalysis.css'

function MTFAnalysis({ mtfData }) {
  if (!mtfData) return null

  const getSignalIcon = (signal) => {
    switch (signal) {
      case 'LONG':
        return <TrendingUp size={16} className="signal-icon-long" />
      case 'SHORT':
        return <TrendingDown size={16} className="signal-icon-short" />
      default:
        return <Minus size={16} className="signal-icon-hold" />
    }
  }

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'LONG':
        return 'var(--success)'
      case 'SHORT':
        return 'var(--error)'
      default:
        return 'var(--text-secondary)'
    }
  }

  const getAlignmentIcon = () => {
    if (mtfData.trend_alignment?.is_aligned) {
      return <CheckCircle size={16} className="aligned-icon" />
    }
    return <AlertTriangle size={16} className="warning-icon" />
  }

  return (
    <div className="card mtf-analysis-card">
      <div className="card-header">
        <h2 className="card-title">Multi-Timeframe Analysis</h2>
        {mtfData.override && (
          <span className="badge badge-warning">MTF Override</span>
        )}
      </div>

      <div className="mtf-content">
        {/* Overall MTF Signal */}
        <div className="mtf-summary">
          <div className="mtf-summary-label">Combined Signal</div>
          <div className="mtf-summary-signal">
            {getSignalIcon(mtfData.mtf_signal)}
            <span 
              className="mtf-signal-text"
              style={{ color: getSignalColor(mtfData.mtf_signal) }}
            >
              {mtfData.mtf_signal}
            </span>
            <span className="mtf-confidence">{mtfData.mtf_confidence?.toFixed(0)}%</span>
          </div>
          <div className="mtf-reason">{mtfData.mtf_reason}</div>
        </div>

        {/* Individual Timeframe Signals */}
        {mtfData.signals_by_timeframe && (
          <div className="mtf-timeframes">
            <div className="mtf-section-label">Timeframe Breakdown</div>
            <div className="mtf-grid">
              {Object.entries(mtfData.signals_by_timeframe).map(([tf, data]) => (
                <div key={tf} className="mtf-timeframe-item">
                  <div className="mtf-tf-header">
                    <span className="mtf-tf-label">{tf}</span>
                    {getSignalIcon(data.signal)}
                  </div>
                  <div className="mtf-tf-details">
                    <span 
                      className="mtf-tf-signal"
                      style={{ color: getSignalColor(data.signal) }}
                    >
                      {data.signal}
                    </span>
                    <span className="mtf-tf-confidence">
                      {data.confidence?.toFixed(0)}%
                    </span>
                  </div>
                  <div className="mtf-tf-strength">
                    <span className={`strength-badge strength-${data.strength?.toLowerCase()}`}>
                      {data.strength}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trend Alignment */}
        {mtfData.trend_alignment && (
          <div className="mtf-alignment">
            <div className="mtf-alignment-header">
              {getAlignmentIcon()}
              <span className="mtf-alignment-title">Trend Alignment</span>
            </div>
            <div className="mtf-alignment-details">
              <div className="mtf-alignment-row">
                <span>Higher TF ({mtfData.trend_alignment.higher_tf}):</span>
                <span className={`trend-${mtfData.trend_alignment.higher_tf_trend?.toLowerCase()}`}>
                  {mtfData.trend_alignment.higher_tf_trend}
                </span>
              </div>
              <div className="mtf-alignment-reason">
                {mtfData.trend_alignment.reason}
              </div>
            </div>
          </div>
        )}

        {/* Alignment Score Meter */}
        <div className="mtf-score-meter">
          <div className="mtf-score-label">
            <span>Alignment Score</span>
            <span className="mtf-score-value">{mtfData.alignment_score?.toFixed(0)}%</span>
          </div>
          <div className="mtf-score-bar">
            <div 
              className="mtf-score-fill"
              style={{ 
                width: `${mtfData.alignment_score}%`,
                background: mtfData.alignment_score > 75 ? 'var(--success)' : 
                           mtfData.alignment_score > 50 ? 'var(--warning)' : 'var(--error)'
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default MTFAnalysis

