import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  Users, 
  Star, 
  Calendar,
  MessageSquare,
  Phone,
  Mail,
  Eye
} from 'lucide-react'
import { getApiUrl } from '../../config/api'

interface DashboardStats {
  total_leads: number
  high_score_leads: number
  this_week_leads: number
  qualified_leads: number
}

interface RecentActivity {
  id: string
  type: 'chat' | 'call' | 'email' | 'lead'
  title: string
  description: string
  timestamp: string
  status: string
}

export default function DashboardHome() {
  const [stats, setStats] = useState<DashboardStats>({
    total_leads: 0,
    high_score_leads: 0,
    this_week_leads: 0,
    qualified_leads: 0
  })
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const loadDashboardData = async () => {
    setIsLoading(true)
    try {
      // Load lead stats
      const statsResponse = await fetch(getApiUrl('/api/leads/stats'))
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      // For now, we'll use mock activity data since we don't have activity endpoints yet
      // In the future, this would come from /api/activity or similar
      const mockActivity: RecentActivity[] = [
        {
          id: '1',
          type: 'lead',
          title: 'New Lead: John Doe',
          description: 'High-scoring lead (85) interested in downtown properties',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          status: 'new'
        },
        {
          id: '2',
          type: 'chat',
          title: 'Chat Session Completed',
          description: 'Qualified lead through website chat - budget $500k-750k',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          status: 'completed'
        },
        {
          id: '3',
          type: 'email',
          title: 'Follow-up Email Sent',
          description: 'Sent property recommendations to jane.smith@gmail.com',
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          status: 'sent'
        },
        {
          id: '4',
          type: 'call',
          title: 'Phone Call Scheduled',
          description: 'Scheduled call with Mike Johnson for tomorrow 2 PM',
          timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
          status: 'scheduled'
        }
      ]
      setRecentActivity(mockActivity)

    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadDashboardData()
  }, [])

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'chat': return <MessageSquare className="h-5 w-5" />
      case 'call': return <Phone className="h-5 w-5" />
      case 'email': return <Mail className="h-5 w-5" />
      case 'lead': return <Users className="h-5 w-5" />
      default: return <Eye className="h-5 w-5" />
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'chat': return 'text-blue-600 bg-blue-100'
      case 'call': return 'text-green-600 bg-green-100'
      case 'email': return 'text-purple-600 bg-purple-100'
      case 'lead': return 'text-orange-600 bg-orange-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'bg-blue-100 text-blue-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'sent': return 'bg-purple-100 text-purple-800'
      case 'scheduled': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffInHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Just now'
    if (diffInHours < 24) return `${diffInHours}h ago`
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays}d ago`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening with your real estate leads.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Leads</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.total_leads}</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="ml-2 text-sm text-green-600">+12% from last week</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Star className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">High Score Leads</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.high_score_leads}</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="ml-2 text-sm text-green-600">+8% from last week</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">This Week</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.this_week_leads}</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="ml-2 text-sm text-green-600">+15% from last week</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Eye className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Qualified</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.qualified_leads}</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="ml-2 text-sm text-green-600">+5% from last week</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
        </div>
        <div className="p-6">
          <div className="flow-root">
            <ul className="-mb-8">
              {recentActivity.map((activity, activityIdx) => (
                <li key={activity.id}>
                  <div className="relative pb-8">
                    {activityIdx !== recentActivity.length - 1 ? (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    ) : null}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${getActivityColor(activity.type)}`}>
                          {getActivityIcon(activity.type)}
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-500">
                            {activity.title}
                          </p>
                          <p className="text-sm text-gray-900">
                            {activity.description}
                          </p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time dateTime={activity.timestamp}>
                            {formatTimeAgo(activity.timestamp)}
                          </time>
                          <div className="mt-1">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                              {activity.status}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors">
              View All Leads
            </button>
            <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors">
              Configure Agent
            </button>
            <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md transition-colors">
              Export Data
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance</h3>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Conversion Rate</span>
              <span className="font-medium">23.5%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Avg Response Time</span>
              <span className="font-medium">2.3 min</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Chat Sessions</span>
              <span className="font-medium">156</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Today's Goals</h3>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">New Leads</span>
              <span className="font-medium text-green-600">12/15</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Follow-ups</span>
              <span className="font-medium text-yellow-600">8/10</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Qualified</span>
              <span className="font-medium text-blue-600">5/8</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 