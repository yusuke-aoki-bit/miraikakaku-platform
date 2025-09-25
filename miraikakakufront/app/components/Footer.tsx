'use client';

import { useRouter } from 'next/navigation';

// Static translations to avoid i18n dependency
const translations = {
  'footer.links.disclaimer': '免責事項'
  'footer.links.terms': '利用規約'
  'footer.links.privacy': 'プライバシーポリシー'
  'footer.copyright': '© 2024 未来価格. All rights reserved.'
  'footer.disclaimer': 'このサイトは投資の助言を行うものではありません。'
};

const t = (key: string, fallback?: string) => translations[key] || fallback || key;

export default function Footer() {
  const router = useRouter(
  const legalLinks = [
    { href: '/disclaimer', label: t('footer.links.disclaimer', '免責事項') }
    { href: '/terms', label: t('footer.links.terms', '利用規約') }
    { href: '/privacy', label: t('footer.links.privacy', 'プライバシーポリシー') }
  ];

  return (
    <footer className="py-8 px-4 border-t" style={{
      backgroundColor: 'rgb(var(--theme-bg-secondary))'
      borderColor: 'rgb(var(--theme-border))'
    }}>
      <div className="max-w-6xl mx-auto">
        {/* Legal Links */}
        <div className="flex flex-wrap justify-center gap-4 mb-6">
          {legalLinks.map((link) => (
            <button
              key={link.href}
              onClick={() => router.push(link.href)}
              className="theme-btn-ghost text-sm hover:underline"
              onMouseEnter={(e) => {
                e.currentTarget.style.color = 'rgb(var(--theme-primary))';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'rgb(var(--theme-text-secondary))';
              }}
            >
              {link.label}
            </button>
          ))}
        </div>

        {/* Copyright */}
        <div className="text-center">
          <p className="theme-body mb-2">
            {t('footer.copyright')}
          </p>
          <p className="theme-caption">
            {t('footer.disclaimer')}
          </p>
        </div>
      </div>
    </footer>
}