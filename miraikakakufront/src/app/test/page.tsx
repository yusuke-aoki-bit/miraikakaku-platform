'use client';

import React from 'react';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-2xl font-bold mb-4">API統合テスト</h1>
      
      <div className="space-y-4">
        <div className="p-4 bg-gray-800 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">基本情報</h2>
          <p>フロントエンド: 正常起動</p>
          <p>API Base URL: https://miraikakaku-api-zbaru5v7za-uc.a.run.app</p>
        </div>
        
        <div className="p-4 bg-gray-800 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">API接続テスト</h2>
          <button 
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
            onClick={async () => {
              try {
                const response = await fetch('https://miraikakaku-api-zbaru5v7za-uc.a.run.app/health');
                const data = await response.json();
                console.log('API Health Check:', data);
                alert(`API応答: ${JSON.stringify(data, null, 2)}`);
              } catch (error) {
                console.error('API Error:', error);
                alert(`API エラー: ${error}`);
              }
            }}
          >
            Health Check テスト
          </button>
        </div>
      </div>
    </div>
  );
}