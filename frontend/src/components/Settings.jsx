import { useState } from 'react'
import { Settings as SettingsIcon, X, Save } from 'lucide-react'
import './Settings.css'

function Settings({ onSettingsChange }) {
  const [isOpen, setIsOpen] = useState(false)
  const [settings, setSettings] = useState({
    strategy: 'TECHNICAL',
    minConfidenceDiff: 15,
    cooldownMinutes: 10,
    enableMTF: true,
    mtfTimeframes: 3,
    showPreviousSignal: true,
    autoRefreshInterval: 30
  })

  const handleChange = (key, value) => {
    const newSettings = { ...settings, [key]: value }
    setSettings(newSettings)
  }

  const handleSave = () => {
    if (onSettingsChange) {
      onSettingsChange(settings)
    }
    setIsOpen(false)
  }

  const handleReset = () => {
    const defaultSettings = {
      strategy: 'TECHNICAL',
      minConfidenceDiff: 15,
      cooldownMinutes: 10,
      enableMTF: true,
      mtfTimeframes: 3,
      showPreviousSignal: true,
      autoRefreshInterval: 30
    }
    setSettings(defaultSettings)
  }

  return (
    <>
      <button 
        className="settings-toggle-btn" 
        onClick={() => setIsOpen(true)}
        title="Signal Settings"
      >
        <SettingsIcon size={18} />
      </button>

      {isOpen && (
        <div className="settings-overlay" onClick={() => setIsOpen(false)}>
          <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
            <div className="settings-header">
              <h2 className="settings-title">Signal Settings</h2>
              <button 
                className="settings-close-btn" 
                onClick={() => setIsOpen(false)}
              >
                <X size={20} />
              </button>
            </div>

            <div className="settings-content">
              {/* Strategy Selection */}
              <div className="settings-section">
                <h3 className="settings-section-title">Trading Strategy</h3>
                <p className="settings-section-desc">
                  Choose your signal generation approach
                </p>

                <div className="strategy-selector">
                  <label 
                    className={`strategy-option ${settings.strategy === 'TECHNICAL' ? 'active' : ''}`}
                    onClick={() => handleChange('strategy', 'TECHNICAL')}
                  >
                    <input
                      type="radio"
                      name="strategy"
                      value="TECHNICAL"
                      checked={settings.strategy === 'TECHNICAL'}
                      onChange={(e) => handleChange('strategy', e.target.value)}
                    />
                    <div className="strategy-content">
                      <span className="strategy-name">📊 Technical Analysis</span>
                      <span className="strategy-desc">RSI, MACD, EMA, Bollinger Bands</span>
                    </div>
                  </label>

                  <label 
                    className={`strategy-option ${settings.strategy === 'SMC' ? 'active' : ''}`}
                    onClick={() => handleChange('strategy', 'SMC')}
                  >
                    <input
                      type="radio"
                      name="strategy"
                      value="SMC"
                      checked={settings.strategy === 'SMC'}
                      onChange={(e) => handleChange('strategy', e.target.value)}
                    />
                    <div className="strategy-content">
                      <span className="strategy-name">🎯 Smart Money Concepts</span>
                      <span className="strategy-desc">Order Blocks, FVG, Market Structure</span>
                    </div>
                  </label>
                </div>
              </div>

              {/* Signal Stability */}
              <div className="settings-section">
                <h3 className="settings-section-title">Signal Stability</h3>
                <p className="settings-section-desc">
                  Control how easily signals can change direction
                </p>

                <div className="setting-item">
                  <label htmlFor="cooldown">
                    Cooldown Period
                    <span className="setting-hint">Minutes between signal flips</span>
                  </label>
                  <div className="setting-input-group">
                    <input
                      id="cooldown"
                      type="range"
                      min="5"
                      max="30"
                      step="5"
                      value={settings.cooldownMinutes}
                      onChange={(e) => handleChange('cooldownMinutes', parseInt(e.target.value))}
                    />
                    <span className="setting-value">{settings.cooldownMinutes} min</span>
                  </div>
                  <div className="setting-labels">
                    <span>More Changes</span>
                    <span>More Stable</span>
                  </div>
                </div>

                <div className="setting-item">
                  <label htmlFor="confidence">
                    Confidence Difference
                    <span className="setting-hint">Required confidence increase to flip</span>
                  </label>
                  <div className="setting-input-group">
                    <input
                      id="confidence"
                      type="range"
                      min="10"
                      max="30"
                      step="5"
                      value={settings.minConfidenceDiff}
                      onChange={(e) => handleChange('minConfidenceDiff', parseInt(e.target.value))}
                    />
                    <span className="setting-value">{settings.minConfidenceDiff}%</span>
                  </div>
                  <div className="setting-labels">
                    <span>Responsive</span>
                    <span>Cautious</span>
                  </div>
                </div>
              </div>

              {/* Multi-Timeframe Analysis */}
              <div className="settings-section">
                <h3 className="settings-section-title">Multi-Timeframe Analysis</h3>
                
                <div className="setting-item">
                  <label className="setting-checkbox">
                    <input
                      type="checkbox"
                      checked={settings.enableMTF}
                      onChange={(e) => handleChange('enableMTF', e.target.checked)}
                    />
                    <span>Enable MTF Confirmation</span>
                  </label>
                  <p className="setting-hint">
                    Analyze multiple timeframes before generating signals
                  </p>
                </div>

                {settings.enableMTF && (
                  <div className="setting-item">
                    <label htmlFor="mtfCount">
                      Timeframes to Analyze
                      <span className="setting-hint">Current timeframe + N higher</span>
                    </label>
                    <div className="setting-input-group">
                      <input
                        id="mtfCount"
                        type="range"
                        min="2"
                        max="4"
                        step="1"
                        value={settings.mtfTimeframes}
                        onChange={(e) => handleChange('mtfTimeframes', parseInt(e.target.value))}
                      />
                      <span className="setting-value">{settings.mtfTimeframes} TFs</span>
                    </div>
                    <div className="setting-labels">
                      <span>Faster</span>
                      <span>More Accurate</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Display Options */}
              <div className="settings-section">
                <h3 className="settings-section-title">Display</h3>
                
                <div className="setting-item">
                  <label className="setting-checkbox">
                    <input
                      type="checkbox"
                      checked={settings.showPreviousSignal}
                      onChange={(e) => handleChange('showPreviousSignal', e.target.checked)}
                    />
                    <span>Show Previous Signal</span>
                  </label>
                </div>

                <div className="setting-item">
                  <label htmlFor="refresh">
                    Auto-Refresh Interval
                    <span className="setting-hint">Seconds between updates</span>
                  </label>
                  <div className="setting-input-group">
                    <input
                      id="refresh"
                      type="range"
                      min="10"
                      max="60"
                      step="10"
                      value={settings.autoRefreshInterval}
                      onChange={(e) => handleChange('autoRefreshInterval', parseInt(e.target.value))}
                    />
                    <span className="setting-value">{settings.autoRefreshInterval}s</span>
                  </div>
                </div>
              </div>

              {/* Presets */}
              <div className="settings-section">
                <h3 className="settings-section-title">Quick Presets</h3>
                <div className="preset-buttons">
                  <button 
                    className="preset-btn"
                    onClick={() => setSettings({
                      ...settings,
                      minConfidenceDiff: 10,
                      cooldownMinutes: 5,
                      mtfTimeframes: 2
                    })}
                  >
                    Day Trader
                    <span>Fast signals</span>
                  </button>
                  <button 
                    className="preset-btn"
                    onClick={() => setSettings({
                      ...settings,
                      minConfidenceDiff: 15,
                      cooldownMinutes: 10,
                      mtfTimeframes: 3
                    })}
                  >
                    Balanced
                    <span>Recommended</span>
                  </button>
                  <button 
                    className="preset-btn"
                    onClick={() => setSettings({
                      ...settings,
                      minConfidenceDiff: 20,
                      cooldownMinutes: 20,
                      mtfTimeframes: 4
                    })}
                  >
                    Swing Trader
                    <span>Stable signals</span>
                  </button>
                </div>
              </div>
            </div>

            <div className="settings-footer">
              <button className="settings-btn settings-btn-secondary" onClick={handleReset}>
                Reset to Default
              </button>
              <button className="settings-btn settings-btn-primary" onClick={handleSave}>
                <Save size={16} />
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default Settings

