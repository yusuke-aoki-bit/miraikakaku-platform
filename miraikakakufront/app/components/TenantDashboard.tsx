'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Building2, Users, BarChart3, Settings,
  CreditCard, Activity, AlertCircle, CheckCircle,
  TrendingUp, Clock, Database,
  Plus, Edit, Eye, EyeOff
} from 'lucide-react';

interface Organization {
  id: string;
  name: string;
  display_name: string;
  plan_type: string;
  status: string;
  enabled_features: string[];
}

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

interface UsageData {
  api_calls: { used: number; limit: number; percentage: number };
  predictions: { used: number; limit: number; percentage: number };
  users: { used: number; limit: number; percentage: number };
  symbols: { used: number; limit: number; percentage: number };
}

interface TenantContextType {
  organization: Organization;
  currentUser: User;
  usage: UsageData;
}

const PlanBadge: React.FC<{ plan: string }> = ({ plan }) => {
  const planConfig = {
    basic: { color: 'bg-blue-100 text-blue-800', icon: '📊', name: 'Basic' },
    professional: { color: 'bg-green-100 text-green-800', icon: '🚀', name: 'Professional' },
    enterprise: { color: 'bg-purple-100 text-purple-800', icon: '👑', name: 'Enterprise' },
    custom: { color: 'bg-yellow-100 text-yellow-800', icon: '⚡', name: 'Custom' }
  };

  const config = planConfig[plan as keyof typeof planConfig] || planConfig.basic;

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
      <span className="mr-1">{config.icon}</span>
      {config.name}
    </div>
  );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const statusConfig = {
    active: { color: 'bg-green-100 text-green-800', icon: <CheckCircle className="w-4 h-4" /> },
    trial: { color: 'bg-yellow-100 text-yellow-800', icon: <Clock className="w-4 h-4" /> },
    suspended: { color: 'bg-red-100 text-red-800', icon: <AlertCircle className="w-4 h-4" /> },
    pending: { color: 'bg-gray-100 text-gray-800', icon: <Clock className="w-4 h-4" /> }
  };

  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
      <span className="mr-2">{config.icon}</span>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </div>
  );
};

const UsageBar: React.FC<{ label: string; used: number; limit: number; unit?: string }> = ({
  label, used, limit, unit = ''
}) => {
  const percentage = limit > 0 ? (used / limit) * 100 : 0;
  const isNearLimit = percentage > 80;
  const isOverLimit = percentage > 100;

  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className={`text-sm ${isOverLimit ? 'text-red-600' : isNearLimit ? 'text-yellow-600' : 'text-gray-600'}`}>
          {used.toLocaleString()}{unit} / {limit.toLocaleString()}{unit}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${
            isOverLimit ? 'bg-red-500' : isNearLimit ? 'bg-yellow-500' : 'bg-blue-500'
          }`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      <div className="text-xs text-gray-500 mt-1">
        {percentage.toFixed(1)}% utilized
      </div>
    </div>
  );
};

const UserRow: React.FC<{
  user: User;
  currentUserId: string;
  onEdit: (user: User) => void;
  onToggleStatus: (user: User) => void;
}> = ({ user, currentUserId, onEdit, onToggleStatus }) => {
  const roleConfig = {
    admin: { color: 'text-red-600 bg-red-50', icon: '👑' },
    manager: { color: 'text-blue-600 bg-blue-50', icon: '⚡' },
    analyst: { color: 'text-green-600 bg-green-50', icon: '📊' },
    viewer: { color: 'text-gray-600 bg-gray-50', icon: '👁️' },
    compliance: { color: 'text-purple-600 bg-purple-50', icon: '🛡️' }
  };

  const config = roleConfig[user.role as keyof typeof roleConfig] || roleConfig.viewer;

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center">
          <div className="flex-shrink-0 h-10 w-10">
            <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold">
              {user.username.substring(0, 2).toUpperCase()}
            </div>
          </div>
          <div className="ml-4">
            <div className="text-sm font-medium text-gray-900">
              {user.full_name || user.username}
              {user.id === currentUserId && (
                <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">You</span>
              )}
            </div>
            <div className="text-sm text-gray-500">{user.email}</div>
          </div>
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${config.color}`}>
          <span className="mr-1">{config.icon}</span>
          {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
          user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {user.is_active ? <CheckCircle className="w-3 h-3 mr-1" /> : <AlertCircle className="w-3 h-3 mr-1" />}
          {user.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : 'Never'}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        {new Date(user.created_at).toLocaleDateString()}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <button
          onClick={() => onEdit(user)}
          className="text-indigo-600 hover:text-indigo-900 mr-3"
          title="Edit User"
        >
          <Edit className="w-4 h-4" />
        </button>
        {user.id !== currentUserId && (
          <button
            onClick={() => onToggleStatus(user)}
            className={`${user.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}`}
            title={user.is_active ? 'Deactivate' : 'Activate'}
          >
            {user.is_active ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </td>
    </tr>
  );
};

export default function TenantDashboard() {
  const [tenantData, setTenantData] = useState<TenantContextType | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState<string | null>(null);

  // Mock data for demonstration
  useEffect(() => {
    const fetchTenantData = async () => {
      try {
        // This would be real API calls in production
        const mockData: TenantContextType = {
          organization: {
            id: '123e4567-e89b-12d3-a456-426614174000',
            name: 'Acme Corporation',
            display_name: 'Acme Corp',
            plan_type: 'enterprise',
            status: 'active',
            enabled_features: [
              'basic_predictions', 'advanced_predictions', 'realtime_streaming',
              'api_access', 'compliance_reports', 'audit_logs', 'sso'
            ]
          },
          currentUser: {
            id: 'user-123',
            email: 'admin@acme.com',
            username: 'admin',
            full_name: 'John Admin',
            role: 'admin',
            is_active: true,
            last_login_at: new Date().toISOString(),
            created_at: '2024-01-15T10:00:00Z'
          },
          usage: {
            api_calls: { used: 45750, limit: 1000000, percentage: 4.6 },
            predictions: { used: 1240, limit: 10000, percentage: 12.4 },
            users: { used: 23, limit: 500, percentage: 4.6 },
            symbols: { used: 127, limit: 1000, percentage: 12.7 }
          }
        };

        const mockUsers: User[] = [
          {
            id: 'user-123',
            email: 'admin@acme.com',
            username: 'admin',
            full_name: 'John Admin',
            role: 'admin',
            is_active: true,
            last_login_at: new Date().toISOString(),
            created_at: '2024-01-15T10:00:00Z'
          },
          {
            id: 'user-456',
            email: 'manager@acme.com',
            username: 'manager',
            full_name: 'Sarah Manager',
            role: 'manager',
            is_active: true,
            last_login_at: new Date(Date.now() - 86400000).toISOString(),
            created_at: '2024-01-20T14:30:00Z'
          },
          {
            id: 'user-789',
            email: 'analyst@acme.com',
            username: 'analyst',
            full_name: 'Mike Analyst',
            role: 'analyst',
            is_active: true,
            last_login_at: new Date(Date.now() - 3600000).toISOString(),
            created_at: '2024-02-01T09:15:00Z'
          },
          {
            id: 'user-101',
            email: 'viewer@acme.com',
            username: 'viewer',
            full_name: 'Lisa Viewer',
            role: 'viewer',
            is_active: false,
            last_login_at: new Date(Date.now() - 604800000).toISOString(),
            created_at: '2024-02-10T16:45:00Z'
          }
        ];

        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate loading

        setTenantData(mockData);
        setUsers(mockUsers);
        setLoading(false);

      } catch (err) {
        setError('Failed to load tenant data');
        setLoading(false);
      }
    };

    fetchTenantData();
  }, []);

  const handleEditUser = useCallback((user: User) => {
    // Implementation for editing user
    if (process.env.NODE_ENV === 'development') {
      console.log('Edit user:', user);
    }
  }, []);

  const handleToggleUserStatus = useCallback((user: User) => {
    // Implementation for toggling user status
    setUsers(prev => prev.map(u =>
      u.id === user.id ? { ...u, is_active: !u.is_active } : u
    ));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading tenant dashboard...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !tenantData) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="mt-2 text-sm text-red-700">{error || 'Failed to load data'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'users', name: 'Users', icon: Users },
    { id: 'settings', name: 'Settings', icon: Settings },
    { id: 'billing', name: 'Billing', icon: CreditCard }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Building2 className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {tenantData.organization.display_name}
                </h1>
                <p className="text-sm text-gray-500">Organization Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <PlanBadge plan={tenantData.organization.plan_type} />
              <StatusBadge status={tenantData.organization.status} />
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Activity className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">API Calls</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {tenantData.usage.api_calls.used.toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">This month</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Predictions</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {tenantData.usage.predictions.used.toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">Today</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Users className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Active Users</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {tenantData.usage.users.used}
                    </p>
                    <p className="text-sm text-gray-500">of {tenantData.usage.users.limit}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <Database className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Symbols Tracked</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {tenantData.usage.symbols.used}
                    </p>
                    <p className="text-sm text-gray-500">of {tenantData.usage.symbols.limit}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Usage Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Overview</h3>
                <div className="space-y-4">
                  <UsageBar
                    label="API Calls (Monthly)"
                    used={tenantData.usage.api_calls.used}
                    limit={tenantData.usage.api_calls.limit}
                  />
                  <UsageBar
                    label="Predictions (Daily)"
                    used={tenantData.usage.predictions.used}
                    limit={tenantData.usage.predictions.limit}
                  />
                  <UsageBar
                    label="Active Users"
                    used={tenantData.usage.users.used}
                    limit={tenantData.usage.users.limit}
                  />
                  <UsageBar
                    label="Tracked Symbols"
                    used={tenantData.usage.symbols.used}
                    limit={tenantData.usage.symbols.limit}
                  />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Enabled Features</h3>
                <div className="space-y-3">
                  {tenantData.organization.enabled_features.map((feature, index) => (
                    <div key={index} className="flex items-center p-3 bg-green-50 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                      <span className="text-sm font-medium text-gray-900">
                        {feature.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                <Plus className="w-4 h-4 mr-2" />
                Add User
              </button>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Login
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <UserRow
                      key={user.id}
                      user={user}
                      currentUserId={tenantData.currentUser.id}
                      onEdit={handleEditUser}
                      onToggleStatus={handleToggleUserStatus}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Organization Settings</h2>

            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Organization Name
                  </label>
                  <input
                    type="text"
                    defaultValue={tenantData.organization.name}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Display Name
                  </label>
                  <input
                    type="text"
                    defaultValue={tenantData.organization.display_name}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Two-Factor Authentication</h4>
                    <p className="text-sm text-gray-500">Require 2FA for all users</p>
                  </div>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Enable
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">Single Sign-On</h4>
                    <p className="text-sm text-gray-500">Configure SAML/OIDC integration</p>
                  </div>
                  <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">
                    Configure
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Billing Tab */}
        {activeTab === 'billing' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Billing & Subscription</h2>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Current Plan</h3>
                  <p className="text-sm text-gray-500">Manage your subscription</p>
                </div>
                <PlanBadge plan={tenantData.organization.plan_type} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 border rounded-lg">
                  <h4 className="font-semibold text-gray-900">Monthly Cost</h4>
                  <p className="text-2xl font-bold text-green-600">$2,499</p>
                  <p className="text-sm text-gray-500">Billed monthly</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <h4 className="font-semibold text-gray-900">Next Billing</h4>
                  <p className="text-2xl font-bold text-blue-600">Oct 15</p>
                  <p className="text-sm text-gray-500">2024</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <h4 className="font-semibold text-gray-900">Payment Method</h4>
                  <p className="text-2xl font-bold text-gray-600">••••</p>
                  <p className="text-sm text-gray-500">Visa ending in 4242</p>
                </div>
              </div>

              <div className="mt-6 flex space-x-4">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  Upgrade Plan
                </button>
                <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">
                  Update Payment Method
                </button>
                <button className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">
                  Download Invoices
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}