import { AlertCircle } from 'lucide-react'
import './ConnectionStatus.css'

function ConnectionStatus({ wsConnected }) {
  if (wsConnected) return null

  return (
    <div className="connection-banner">
      <AlertCircle size={18} />
      <span>WebSocket disconnected. Updates paused. Make sure backend is running on port 8000.</span>
    </div>
  )
}

export default ConnectionStatus

