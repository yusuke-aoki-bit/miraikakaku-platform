'use client';

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const languages = [
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
    { code: 'en', name: 'English', flag: '🇺🇸' }
  ];

  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];

  const handleLanguageChange = (langCode: string) => {
    i18n.changeLanguage(langCode);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors"
        style={{
          backgroundColor: 'var(--yt-music-surface-variant)',
          color: 'var(--yt-music-text-primary)',
          border: '1px solid var(--yt-music-border)'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-variant)';
        }}
      >
        <Globe className="w-4 h-4" />
        <span className="text-sm font-medium">
          {currentLanguage?.flag} {currentLanguage?.name}
        </span>
      </button>

      {isOpen && (
        <div
          className="absolute top-full right-0 mt-2 min-w-[140px] rounded-lg shadow-lg z-50"
          style={{
            backgroundColor: 'var(--yt-music-surface)',
            border: '1px solid var(--yt-music-border)'
          }}
        >
          {languages.map((language) => (
            <button
              key={language.code}
              onClick={() => handleLanguageChange(language.code)}
              className={`w-full text-left px-4 py-3 flex items-center space-x-3 transition-colors first:rounded-t-lg last:rounded-b-lg ${
                language.code === i18n.language ? 'font-semibold' : ''
              }`}
              style={{
                color: language.code === i18n.language
                  ? 'var(--yt-music-primary)'
                  : 'var(--yt-music-text-primary)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--yt-music-surface-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <span className="text-base">{language.flag}</span>
              <span className="text-sm">{language.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}