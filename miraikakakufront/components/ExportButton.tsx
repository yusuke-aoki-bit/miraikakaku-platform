'use client';

import { useState } from 'react';
import { ExportFormat, handleExport } from '@/lib/exportUtils';

/**
 * エクスポートボタンコンポーネント
 * CSV、JSON、Excelフォーマットでのデータエクスポートをサポート
 */

interface ExportButtonProps<T> {
  data: T[];
  filename: string;
  columns?: { key: keyof T; label: string }[];
  buttonText?: string;
  className?: string;
}

export function ExportButton<T extends Record<string, any>>({
  data,
  filename,
  columns,
  buttonText = 'エクスポート',
  className = ''
}: ExportButtonProps<T>) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const formats: { value: ExportFormat; label: string; icon: string; description: string }[] = [
    {
      value: 'csv',
      label: 'CSV',
      icon: '📄',
      description: 'Excel、Google Sheetsで開ける汎用形式'
    },
    {
      value: 'excel',
      label: 'Excel',
      icon: '📊',
      description: 'Microsoft Excel形式'
    },
    {
      value: 'json',
      label: 'JSON',
      icon: '🔧',
      description: 'プログラマー向けデータ形式'
    },
  ];

  const doExport = async (format: ExportFormat) => {
    setIsExporting(true);
    try {
      handleExport({
        data,
        filename,
        format,
        columns,
        onExport: () => {
          setIsOpen(false);
          setIsExporting(false);
        }
      });
    } catch (error) {
      console.error('Export failed:', error);
      alert('エクスポートに失敗しました');
      setIsExporting(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={data.length === 0}
        className={`flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors ${className}`}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span>{buttonText}</span>
        {data.length > 0 && (
          <span className="text-xs opacity-80">
            ({data.length.toLocaleString()}件)
          </span>
        )}
      </button>

      {/* ドロップダウンメニュー */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 z-20 overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                エクスポート形式を選択
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                データを以下の形式でダウンロードできます
              </p>
            </div>

            <div className="p-2">
              {formats.map(format => (
                <button
                  key={format.value}
                  onClick={() => doExport(format.value)}
                  disabled={isExporting}
                  className="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">{format.icon}</span>
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900 dark:text-white">
                        {format.label}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {format.description}
                      </div>
                    </div>
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </button>
              ))}
            </div>

            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border-t border-blue-200 dark:border-blue-800">
              <p className="text-xs text-blue-800 dark:text-blue-200">
                💡 <strong>ヒント:</strong> CSVは最も互換性が高く、Excelやスプレッドシートで簡単に開けます。
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

/**
 * シンプルなエクスポートボタン（フォーマット固定）
 */
export function QuickExportButton<T extends Record<string, any>>({
  data,
  filename,
  format = 'csv',
  columns,
  icon = true
}: {
  data: T[];
  filename: string;
  format?: ExportFormat;
  columns?: { key: keyof T; label: string }[];
  icon?: boolean;
}) {
  const [isExporting, setIsExporting] = useState(false);

  const doExport = async () => {
    setIsExporting(true);
    try {
      handleExport({
        data,
        filename,
        format,
        columns,
        onExport: () => setIsExporting(false)
      });
    } catch (error) {
      console.error('Export failed:', error);
      alert('エクスポートに失敗しました');
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={doExport}
      disabled={data.length === 0 || isExporting}
      className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300 text-sm font-medium rounded transition-colors"
      title={`${format.toUpperCase()}でエクスポート`}
    >
      {icon && (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )}
      <span>{isExporting ? 'エクスポート中...' : format.toUpperCase()}</span>
    </button>
  );
}
