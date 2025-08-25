'use client';

import { useEffect, useRef } from 'react';

interface ContentSection {
  id: string;
  title: string;
  content: string | string[];
  subsections?: ContentSection[];
}

interface LegalContentProps {
  sections: ContentSection[];
  onSectionInView?: (sectionId: string) => void;
}

export default function LegalContent({ sections, onSectionInView }: LegalContentProps) {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sectionRefs = useRef<Map<string, HTMLElement>>(new Map());

  useEffect(() => {
    // Intersection Observer for tracking which section is in view
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.target instanceof HTMLElement) {
            const sectionId = entry.target.getAttribute('data-section-id');
            if (sectionId && onSectionInView) {
              onSectionInView(sectionId);
            }
          }
        });
      },
      {
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
      }
    );

    // Observe all section elements
    sectionRefs.current.forEach((element) => {
      if (observerRef.current) {
        observerRef.current.observe(element);
      }
    });

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [onSectionInView]);

  const setSectionRef = (id: string, element: HTMLElement | null) => {
    if (element) {
      sectionRefs.current.set(id, element);
    } else {
      sectionRefs.current.delete(id);
    }
  };

  const renderContent = (content: string | string[]) => {
    if (Array.isArray(content)) {
      return (
        <div className="space-y-4">
          {content.map((paragraph, index) => (
            <div key={index}>
              {paragraph.startsWith('・') || paragraph.startsWith('•') ? (
                <ul className="list-none space-y-2">
                  {paragraph.split('\n').filter(item => item.trim()).map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-start">
                      <span className="w-2 h-2 bg-accent-primary rounded-full mt-3 mr-3 flex-shrink-0"></span>
                      <span className="text-text-primary leading-relaxed">
                        {item.replace(/^[・•]\s*/, '')}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : paragraph.match(/^\d+\./) ? (
                <ol className="list-none space-y-2 counter-reset-item">
                  {paragraph.split('\n').filter(item => item.trim()).map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-start counter-increment-item">
                      <span className="w-6 h-6 bg-accent-primary text-white text-xs font-medium rounded-full flex items-center justify-center mt-1 mr-3 flex-shrink-0">
                        {itemIndex + 1}
                      </span>
                      <span className="text-text-primary leading-relaxed">
                        {item.replace(/^\d+\.\s*/, '')}
                      </span>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="text-text-primary leading-relaxed text-base">
                  {paragraph}
                </p>
              )}
            </div>
          ))}
        </div>
      );
    } else {
      // Handle single string content with basic formatting
      const formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-text-primary">$1</strong>')
        .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
        .replace(/「(.*?)」/g, '<span class="text-accent-primary font-medium">「$1」</span>');

      return (
        <div
          className="text-text-primary leading-relaxed text-base prose prose-gray max-w-none"
          dangerouslySetInnerHTML={{ __html: formattedContent }}
        />
      );
    }
  };

  const renderSection = (section: ContentSection, level: number = 2) => {
    const HeadingTag = `h${Math.min(level, 6)}` as keyof JSX.IntrinsicElements;
    const headingClasses = {
      2: 'text-2xl font-bold text-text-primary mt-12 mb-6 pb-3 border-b border-border-primary',
      3: 'text-xl font-semibold text-text-primary mt-8 mb-4',
      4: 'text-lg font-medium text-text-primary mt-6 mb-3',
      5: 'text-base font-medium text-text-primary mt-4 mb-2',
      6: 'text-sm font-medium text-text-primary mt-3 mb-2'
    };

    return (
      <section
        key={section.id}
        id={section.id}
        ref={(el) => setSectionRef(section.id, el)}
        data-section-id={section.id}
        className="scroll-mt-24"
      >
        <HeadingTag className={headingClasses[level as keyof typeof headingClasses] || headingClasses[6]}>
          {section.title}
        </HeadingTag>

        <div className="mb-8">
          {renderContent(section.content)}
        </div>

        {section.subsections && section.subsections.length > 0 && (
          <div className="ml-6 border-l-2 border-accent-primary/20 pl-6">
            {section.subsections.map((subsection) => 
              renderSection(subsection, level + 1)
            )}
          </div>
        )}
      </section>
    );
  };

  return (
    <article className="prose prose-lg max-w-none">
      {sections.map((section) => renderSection(section))}

      {/* フッター */}
      <footer className="mt-16 pt-8 border-t border-border-primary">
        <div className="bg-surface-background rounded-lg p-6 text-center">
          <h3 className="text-lg font-semibold text-text-primary mb-3">
            お問い合わせ
          </h3>
          <p className="text-text-secondary mb-4">
            本文書の内容についてご質問やご不明な点がございましたら、
            お気軽にお問い合わせください。
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a
              href="mailto:support@miraikakaku.com"
              className="inline-flex items-center justify-center px-4 py-2 bg-accent-primary hover:bg-accent-primary/90 text-white rounded-lg font-medium transition-colors"
            >
              メールでお問い合わせ
            </a>
            <a
              href="/contact"
              className="inline-flex items-center justify-center px-4 py-2 border border-border-primary hover:bg-surface-background text-text-primary rounded-lg font-medium transition-colors"
            >
              お問い合わせフォーム
            </a>
          </div>
        </div>
      </footer>
    </article>
  );
}