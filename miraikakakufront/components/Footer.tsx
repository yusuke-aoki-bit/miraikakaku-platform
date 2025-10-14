'use client';

import { useRouter } from 'next/navigation';

export default function Footer() {
  const router = useRouter();
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    '取引所': [
      { name: '東京証券取引所', path: '/exchange/tse' },
      { name: 'NASDAQ', path: '/exchange/nasdaq' },
      { name: 'NYSE', path: '/exchange/nyse' },
      { name: '暗号通貨', path: '/exchange/crypto' },
    ],
    '機能': [
      { name: 'ランキング', path: '/rankings' },
      { name: '検索', path: '/search?q=' },
    ],
    '法的情報': [
      { name: '利用規約', path: '/terms' },
      { name: 'プライバシーポリシー', path: '/privacy' },
    ],
  };

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Logo and Description */}
          <div className="md:col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">M</span>
              </div>
              <span className="text-xl font-bold text-white">Miraikakaku</span>
            </div>
            <p className="text-sm text-gray-400">
              AI技術を活用した次世代株価予測プラットフォーム
            </p>
          </div>

          {/* Footer Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="text-white font-semibold mb-4">{category}</h3>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.path}>
                    <button
                      onClick={() => router.push(link.path)}
                      className="text-gray-400 hover:text-white transition-colors text-sm"
                    >
                      {link.name}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Disclaimer */}
        <div className="border-t border-gray-800 pt-8 mb-8">
          <div className="bg-yellow-900/20 border-l-4 border-yellow-500 p-4 rounded">
            <h4 className="text-yellow-400 font-semibold mb-2">重要な免責事項</h4>
            <p className="text-sm text-gray-400">
              当サービスが提供する情報は投資の助言や推奨を目的としたものではありません。
              すべての投資判断はご自身の責任において行ってください。
              当サービスの利用によって生じた損害について、当社は一切の責任を負いません。
            </p>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-gray-400 mb-4 md:mb-0">
            © {currentYear} Miraikakaku. All rights reserved.
          </p>
          <div className="flex space-x-6">
            <button
              onClick={() => router.push('/terms')}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              利用規約
            </button>
            <button
              onClick={() => router.push('/privacy')}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              プライバシーポリシー
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
}
