'use client';

import React from 'react';
import { ShoppingCart, DollarSign } from 'lucide-react';

export function AmazonAssociatesWidget() {
  return (
    <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg p-6">
      <div className="flex items-center mb-4">
        <ShoppingCart className="w-6 h-6 text-orange-600 mr-2" />
        <h3 className="text-xl font-semibold text-gray-900">
          Investment Resources
        </h3>
      </div>

      <div className="space-y-4">
        <div className="bg-white rounded-md p-4 border border-orange-100">
          <h4 className="font-medium text-gray-900 mb-2">
            📚 Recommended Investment Books
          </h4>
          <p className="text-gray-700 text-sm mb-3">
            Enhance your investment knowledge with these bestselling books on stock analysis and market strategies.
          </p>
          <button className="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 px-4 rounded-md transition-colors text-sm font-medium">
            View Book Recommendations
          </button>
        </div>

        <div className="bg-white rounded-md p-4 border border-orange-100">
          <h4 className="font-medium text-gray-900 mb-2">
            🛠️ Trading Tools & Software
          </h4>
          <p className="text-gray-700 text-sm mb-3">
            Professional-grade tools for technical analysis, portfolio management, and market research.
          </p>
          <button className="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 px-4 rounded-md transition-colors text-sm font-medium">
            Shop Investment Tools
          </button>
        </div>
      </div>

      <p className="text-xs text-gray-500 mt-4">
        * As an Amazon Associate, we earn from qualifying purchases.
      </p>
    </div>
  );
}

export function GoogleAdSenseWidget() {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
      <div className="flex items-center mb-4">
        <DollarSign className="w-6 h-6 text-blue-600 mr-2" />
        <h3 className="text-xl font-semibold text-gray-900">
          Advertisement
        </h3>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-4 min-h-[250px] flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-2">📊</div>
          <p className="text-sm">
            Advertisement Space
          </p>
          <p className="text-xs mt-1">
            Google AdSense placement
          </p>
        </div>
      </div>

      <p className="text-xs text-gray-500 mt-4">
        Advertisement
      </p>
    </div>
  );
}

export function PremiumMembershipWidget() {
  return (
    <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
      <div className="flex items-center mb-4">
        <div className="w-6 h-6 mr-2">⭐</div>
        <h3 className="text-xl font-semibold text-gray-900">
          Premium Membership
        </h3>
      </div>

      <div className="space-y-4">
        <div className="bg-white rounded-md p-4 border border-purple-100">
          <h4 className="font-medium text-gray-900 mb-2">
            🚀 Unlock Advanced Features
          </h4>
          <ul className="text-sm text-gray-700 space-y-2 mb-4">
            <li>• Real-time advanced predictions</li>
            <li>• Portfolio analysis tools</li>
            <li>• Priority customer support</li>
            <li>• Ad-free experience</li>
          </ul>
          <button className="w-full bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-md transition-colors text-sm font-medium">
            Upgrade to Premium
          </button>
        </div>
      </div>

      <p className="text-xs text-gray-500 mt-4">
        Support the development of our AI prediction platform
      </p>
    </div>
  );
}