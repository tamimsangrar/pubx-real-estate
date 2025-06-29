import { Routes, Route } from 'react-router-dom'

export default function AdminDashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
        
        <Routes>
          <Route path="/" element={<div>Dashboard Home - Coming Soon</div>} />
          <Route path="/leads" element={<div>Leads Management - Coming Soon</div>} />
          <Route path="/settings" element={<div>Settings - Coming Soon</div>} />
        </Routes>
      </div>
    </div>
  )
} 