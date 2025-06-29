import React, { useState, useEffect } from 'react'
import { Save, RefreshCw, Brain, MessageSquare, Settings } from 'lucide-react'
import { getApiUrl, API_CONFIG } from '../../config/api'

interface AgentConfig {
  personality: string
  system_prompt: string
  temperature: number
  model: string
  max_tokens: number
  services: string[]
  tools_enabled: boolean
}

export default function AgentConfig() {
  const [config, setConfig] = useState<AgentConfig>({
    personality: 'Professional and friendly real estate assistant',
    system_prompt: 'You are a helpful real estate assistant. Help users find properties, answer questions about the market, and qualify leads.',
    temperature: 0.7,
    model: 'gpt-4-turbo',
    max_tokens: 1000,
    services: ['property_search', 'lead_qualification', 'market_info'],
    tools_enabled: true
  })

  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState('')

  const personalityPresets = [
    {
      name: 'Professional',
      description: 'Formal and business-like',
      value: 'Professional and formal real estate consultant with extensive market knowledge.'
    },
    {
      name: 'Friendly',
      description: 'Warm and approachable',
      value: 'Friendly and approachable real estate assistant who makes clients feel comfortable.'
    },
    {
      name: 'Expert',
      description: 'Technical and detailed',
      value: 'Expert real estate advisor with deep market insights and analytical approach.'
    },
    {
      name: 'Casual',
      description: 'Relaxed and conversational',
      value: 'Casual and conversational real estate helper who speaks like a trusted friend.'
    }
  ]

  const modelOptions = [
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo (Recommended)' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' }
  ]

  const serviceOptions = [
    { value: 'property_search', label: 'Property Search' },
    { value: 'lead_qualification', label: 'Lead Qualification' },
    { value: 'market_info', label: 'Market Information' },
    { value: 'scheduling', label: 'Appointment Scheduling' },
    { value: 'mortgage_calc', label: 'Mortgage Calculator' }
  ]

  const loadConfig = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(getApiUrl('/api/config'))
      if (response.ok) {
        const data = await response.json()
        setConfig(data)
        setMessage('Configuration loaded successfully')
      } else {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
    } catch (error) {
      setMessage('Error loading configuration')
      console.error('Error loading config:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const saveConfig = async () => {
    setIsSaving(true)
    try {
      const response = await fetch(getApiUrl('/api/config'), {
        method: 'POST',
        headers: API_CONFIG.DEFAULT_HEADERS,
        body: JSON.stringify(config)
      })
      
      if (response.ok) {
        const result = await response.json()
        setMessage(result.message || 'Configuration saved successfully')
      } else {
        const errorData = await response.json()
        setMessage(errorData.detail || 'Error saving configuration')
      }
    } catch (error) {
      setMessage('Error saving configuration')
      console.error('Error saving config:', error)
    } finally {
      setIsSaving(false)
    }
  }

  useEffect(() => {
    loadConfig()
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent Configuration</h1>
          <p className="text-gray-600">Customize your AI agent's personality and behavior</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={loadConfig}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={saveConfig}
            disabled={isSaving}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <Save className="w-4 h-4 mr-2" />
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-md ${
          message.includes('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
        }`}>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Personality Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <Brain className="w-5 h-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Personality</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Personality Presets
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {personalityPresets.map((preset) => (
                  <button
                    key={preset.name}
                    onClick={() => setConfig({ ...config, personality: preset.value })}
                    className={`p-3 text-left rounded-lg border transition-colors ${
                      config.personality === preset.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-sm">{preset.name}</div>
                    <div className="text-xs text-gray-500">{preset.description}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Personality
              </label>
              <textarea
                value={config.personality}
                onChange={(e) => setConfig({ ...config, personality: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Describe the agent's personality..."
              />
            </div>
          </div>
        </div>

        {/* System Prompt */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <MessageSquare className="w-5 h-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">System Prompt</h3>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Instructions for the AI
            </label>
            <textarea
              value={config.system_prompt}
              onChange={(e) => setConfig({ ...config, system_prompt: e.target.value })}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter system instructions for the AI agent..."
            />
            <p className="mt-2 text-sm text-gray-500">
              This prompt defines how the AI should behave and what it should prioritize.
            </p>
          </div>
        </div>

        {/* Model Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <Settings className="w-5 h-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Model Settings</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Model
              </label>
              <select
                value={config.model}
                onChange={(e) => setConfig({ ...config, model: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                {modelOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature: {config.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={config.temperature}
                onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Focused</span>
                <span>Balanced</span>
                <span>Creative</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Tokens
              </label>
              <input
                type="number"
                value={config.max_tokens}
                onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                min="100"
                max="4000"
              />
            </div>
          </div>
        </div>

        {/* Services & Tools */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <Settings className="w-5 h-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Services & Tools</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Available Services
              </label>
              <div className="space-y-2">
                {serviceOptions.map((service) => (
                  <label key={service.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.services.includes(service.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setConfig({
                            ...config,
                            services: [...config.services, service.value]
                          })
                        } else {
                          setConfig({
                            ...config,
                            services: config.services.filter(s => s !== service.value)
                          })
                        }
                      }}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">{service.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.tools_enabled}
                  onChange={(e) => setConfig({ ...config, tools_enabled: e.target.checked })}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">
                  Enable External Tools
                </span>
              </label>
              <p className="mt-1 text-xs text-gray-500">
                Allow the agent to use external APIs and services
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 