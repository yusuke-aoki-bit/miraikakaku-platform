'use client';

import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="youtube-glass px-6 py-4 text-xs text-gray-400">
      <div className="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
        <p>&copy; {currentYear} Miraikakaku Inc. All rights reserved.</p>
        <div className="flex items-center space-x-4">
          <Link href="/terms-of-service" className="hover:text-white transition-colors">利用規約</Link>
          <Link href="/privacy-policy" className="hover:text-white transition-colors">プライバシーポリシー</Link>
          <Link href="/disclaimer" className="hover:text-white transition-colors">免責事項</Link>
        </div>
      </div>
    </footer>
  );
}
