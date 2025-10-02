import { Activity, RefreshCw } from 'lucide-react'
import './Header.css'

function Header({ lastUpdate, wsConnected, onRefresh }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <Activity className="header-icon" />
          <h1 className="header-title">Koko Trader</h1>
        </div>
        
        <div className="header-right">
          {lastUpdate && (
            <span className="last-update">
              Last update: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          
          <div className={`ws-status ${wsConnected ? 'connected' : 'disconnected'}`}>
            <div className="status-dot"></div>
            {wsConnected ? 'Live' : 'Offline'}
          </div>
          
          <button className="refresh-btn" onClick={onRefresh}>
            <RefreshCw size={18} />
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header


