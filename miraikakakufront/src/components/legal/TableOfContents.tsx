'use client';

import { useState, useEffect } from 'react';
import { ChevronDownIcon, ChevronUpIcon, ListBulletIcon } from '@heroicons/react/24/outline';

interface ContentSection {
  id: string;
  title: string;
  content: string | string[];
  subsections?: ContentSection[];
}

interface TableOfContentsProps {
  sections: ContentSection[];
  activeSection?: string;
}

export default function TableOfContents({ sections, activeSection }: TableOfContentsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const offset = 100; // Header height offset
      const top = element.offsetTop - offset;
      window.scrollTo({
        top,
        behavior: 'smooth'
      });
    }
    
    // Close mobile menu after clicking
    if (isMobile) {
      setIsOpen(false);
    }
  };

  const renderTocItems = (items: ContentSection[], level = 0) => {
    return items.map((section) => (
      <div key={section.id}>
        <button
          onClick={() => scrollToSection(section.id)}
          className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
            activeSection === section.id
              ? 'bg-accent-primary text-white font-medium'
              : 'text-text-secondary hover:text-text-primary hover:bg-surface-background'
          } ${level > 0 ? `ml-${level * 4}` : ''}`}
        >
          {section.title}
        </button>
        
        {section.subsections && section.subsections.length > 0 && (
          <div className="ml-4 border-l-2 border-border-primary pl-2 mt-1 mb-2">
            {renderTocItems(section.subsections, level + 1)}
          </div>
        )}
      </div>
    ));
  };

  if (isMobile) {
    // モバイル版: アコーディオン形式
    return (
      <div className="lg:hidden bg-surface-elevated border border-border-primary rounded-lg mb-8">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between p-4 text-left"
        >
          <div className="flex items-center">
            <ListBulletIcon className="w-5 h-5 text-accent-primary mr-2" />
            <span className="font-medium text-text-primary">目次</span>
          </div>
          {isOpen ? (
            <ChevronUpIcon className="w-5 h-5 text-text-secondary" />
          ) : (
            <ChevronDownIcon className="w-5 h-5 text-text-secondary" />
          )}
        </button>

        {isOpen && (
          <div className="border-t border-border-primary p-4 max-h-80 overflow-y-auto">
            <nav className="space-y-1">
              {renderTocItems(sections)}
            </nav>
          </div>
        )}
      </div>
    );
  }

  // デスクトップ版: 固定サイドバー
  return (
    <aside className="hidden lg:block w-80">
      <div className="sticky top-24 bg-surface-elevated border border-border-primary rounded-lg p-6">
        <div className="flex items-center mb-4">
          <ListBulletIcon className="w-5 h-5 text-accent-primary mr-2" />
          <h3 className="font-semibold text-text-primary">目次</h3>
        </div>

        <nav className="space-y-1 max-h-[calc(100vh-200px)] overflow-y-auto">
          {renderTocItems(sections)}
        </nav>

        {/* 進捗インジケーター */}
        <div className="mt-6 pt-4 border-t border-border-primary">
          <div className="text-xs text-text-secondary mb-2">読み進み度</div>
          <div className="w-full bg-surface-background rounded-full h-2">
            <div 
              className="bg-accent-primary h-2 rounded-full transition-all duration-300"
              style={{
                width: activeSection 
                  ? `${((sections.findIndex(s => s.id === activeSection) + 1) / sections.length) * 100}%`
                  : '0%'
              }}
            />
          </div>
          <div className="text-xs text-text-secondary mt-1">
            {activeSection && sections.findIndex(s => s.id === activeSection) + 1} / {sections.length} セクション
          </div>
        </div>

        {/* ページトップボタン */}
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="w-full mt-4 px-3 py-2 text-sm text-accent-primary hover:bg-accent-primary/10 border border-accent-primary/20 rounded-lg transition-colors"
        >
          ページトップに戻る
        </button>
      </div>
    </aside>
  );
}