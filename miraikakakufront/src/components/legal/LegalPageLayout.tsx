'use client';

import { useState } from 'react';
import PageHeader from './PageHeader';
import LegalContent from './LegalContent';
import TableOfContents from './TableOfContents';

interface ContentSection {
  id: string;
  title: string;
  content: string | string[];
  subsections?: ContentSection[];
}

interface LegalPageLayoutProps {
  title: string;
  lastUpdated: string;
  description?: string;
  icon?: 'terms' | 'privacy';
  sections: ContentSection[];
}

export default function LegalPageLayout({
  title,
  lastUpdated,
  description,
  icon,
  sections
}: LegalPageLayoutProps) {
  const [activeSection, setActiveSection] = useState<string>('');

  const handleSectionInView = (sectionId: string) => {
    setActiveSection(sectionId);
  };

  return (
    <div className="min-h-screen bg-surface-background">
      {/* ページヘッダー */}
      <PageHeader
        title={title}
        lastUpdated={lastUpdated}
        description={description}
        icon={icon}
      />

      {/* メインコンテンツ */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* 目次 */}
          <TableOfContents
            sections={sections}
            activeSection={activeSection}
          />

          {/* コンテンツ */}
          <main className="flex-1 max-w-4xl">
            <LegalContent
              sections={sections}
              onSectionInView={handleSectionInView}
            />
          </main>
        </div>
      </div>

      {/* ページフッター */}
      <footer className="bg-surface-elevated border-t border-border-primary mt-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center space-x-6 text-sm">
              <a
                href="/terms"
                className="text-text-secondary hover:text-accent-primary transition-colors"
              >
                利用規約
              </a>
              <a
                href="/privacy"
                className="text-text-secondary hover:text-accent-primary transition-colors"
              >
                プライバシーポリシー
              </a>
              <a
                href="/contact"
                className="text-text-secondary hover:text-accent-primary transition-colors"
              >
                お問い合わせ
              </a>
            </div>
            
            <div className="text-xs text-text-secondary">
              © {new Date().getFullYear()} 未来価格分析. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}