import './SymbolSelector.css'

const SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
const TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']

function SymbolSelector({ symbol, timeframe, onSymbolChange, onTimeframeChange }) {
  return (
    <div className="symbol-selector">
      <div className="selector-group">
        <label>Symbol</label>
        <select value={symbol} onChange={(e) => onSymbolChange(e.target.value)}>
          {SYMBOLS.map(sym => (
            <option key={sym} value={sym}>{sym}</option>
          ))}
        </select>
      </div>
      
      <div className="selector-group">
        <label>Timeframe</label>
        <select value={timeframe} onChange={(e) => onTimeframeChange(e.target.value)}>
          {TIMEFRAMES.map(tf => (
            <option key={tf} value={tf}>{tf}</option>
          ))}
        </select>
      </div>
    </div>
  )
}

export default SymbolSelector


