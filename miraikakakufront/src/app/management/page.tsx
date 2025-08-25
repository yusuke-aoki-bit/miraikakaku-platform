'use client';

import { useState } from 'react';
import { 
  UserIcon, 
  ShieldCheckIcon, 
  BellIcon, 
  CreditCardIcon, 
  TrashIcon 
} from '@heroicons/react/24/outline';

import ProfileTab from '@/components/management/ProfileTab';
import SecurityTab from '@/components/management/SecurityTab';
import NotificationsTab from '@/components/management/NotificationsTab';
import PlanBillingTab from '@/components/management/PlanBillingTab';
import DeleteAccountTab from '@/components/management/DeleteAccountTab';

type TabType = 'profile' | 'security' | 'notifications' | 'billing' | 'delete';

const tabs = [
  {
    id: 'profile' as TabType,
    name: 'プロフィール',
    icon: UserIcon,
    description: '基本情報の管理',
  },
  {
    id: 'security' as TabType,
    name: 'セキュリティ',
    icon: ShieldCheckIcon,
    description: 'パスワード・認証設定',
  },
  {
    id: 'notifications' as TabType,
    name: '通知設定',
    icon: BellIcon,
    description: '通知の管理',
  },
  {
    id: 'billing' as TabType,
    name: 'プランと請求',
    icon: CreditCardIcon,
    description: 'サブスクリプション管理',
  },
  {
    id: 'delete' as TabType,
    name: 'アカウント削除',
    icon: TrashIcon,
    description: 'アカウントの削除',
  },
];

export default function ManagementPage() {
  const [activeTab, setActiveTab] = useState<TabType>('profile');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <ProfileTab />;
      case 'security':
        return <SecurityTab />;
      case 'notifications':
        return <NotificationsTab />;
      case 'billing':
        return <PlanBillingTab />;
      case 'delete':
        return <DeleteAccountTab />;
      default:
        return <ProfileTab />;
    }
  };

  return (
    <div className="min-h-screen bg-surface-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary">アカウント管理</h1>
          <p className="mt-2 text-text-secondary">
            プロフィール、セキュリティ、通知設定などを管理できます
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          {/* 左側: 垂直ナビゲーション */}
          <div className="w-full lg:w-64 flex-shrink-0">
            <div className="bg-surface-elevated rounded-lg border border-border-primary overflow-hidden">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const isActive = activeTab === tab.id;
                  const Icon = tab.icon;
                  
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-4 py-3 text-left transition-colors ${
                        isActive
                          ? 'bg-accent-primary text-white border-r-2 border-accent-primary'
                          : 'text-text-secondary hover:text-text-primary hover:bg-surface-background'
                      }`}
                    >
                      <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-white' : 'text-current'}`} />
                      <div className="flex-1">
                        <div className={`font-medium ${isActive ? 'text-white' : 'text-text-primary'}`}>
                          {tab.name}
                        </div>
                        <div className={`text-xs mt-0.5 ${isActive ? 'text-white/80' : 'text-text-secondary'}`}>
                          {tab.description}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* モバイル用の注意書き */}
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg lg:hidden">
              <p className="text-sm text-blue-800">
                💡 設定を変更した後は「保存」ボタンを押してください
              </p>
            </div>
          </div>

          {/* 右側: コンテンツエリア */}
          <div className="flex-1">
            <div className="bg-surface-elevated rounded-lg border border-border-primary">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}