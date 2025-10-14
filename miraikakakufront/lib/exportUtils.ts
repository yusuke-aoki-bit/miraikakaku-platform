/**
 * データエクスポートユーティリティ
 * CSV、Excel、PDF形式でのエクスポートをサポート
 */

export type ExportFormat = 'csv' | 'json' | 'excel';

/**
 * CSVエクスポート
 */
export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columns?: { key: keyof T; label: string }[]
) {
  if (data.length === 0) {
    alert('エクスポートするデータがありません');
    return;
  }

  // カラム定義がない場合は、最初のオブジェクトのキーを使用
  const cols = columns || Object.keys(data[0]).map(key => ({
    key: key as keyof T,
    label: key
  }));

  // ヘッダー行
  const headers = cols.map(col => `"${col.label}"`).join(',');

  // データ行
  const rows = data.map(item =>
    cols.map(col => {
      const value = item[col.key];
      // 値をCSV形式でエスケープ
      if (value === null || value === undefined) return '""';
      const stringValue = String(value);
      // ダブルクォートとカンマを含む場合はエスケープ
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      return `"${stringValue}"`;
    }).join(',')
  ).join('\n');

  // BOM付きでUTF-8エンコード
  const csv = '\uFEFF' + headers + '\n' + rows;

  // ダウンロード
  downloadFile(csv, `${filename}.csv`, 'text/csv;charset=utf-8;');
}

/**
 * JSONエクスポート
 */
export function exportToJSON<T>(
  data: T[],
  filename: string
) {
  if (data.length === 0) {
    alert('エクスポートするデータがありません');
    return;
  }

  const json = JSON.stringify(data, null, 2);
  downloadFile(json, `${filename}.json`, 'application/json');
}

/**
 * Excel形式エクスポート（HTML table形式）
 */
export function exportToExcel<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columns?: { key: keyof T; label: string }[]
) {
  if (data.length === 0) {
    alert('エクスポートするデータがありません');
    return;
  }

  const cols = columns || Object.keys(data[0]).map(key => ({
    key: key as keyof T,
    label: key
  }));

  // HTMLテーブル形式で作成
  let html = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">';
  html += '<head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet>';
  html += '<x:Name>Sheet1</x:Name>';
  html += '<x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet>';
  html += '</x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]-->';
  html += '<meta charset="UTF-8">';
  html += '</head><body>';
  html += '<table border="1">';

  // ヘッダー
  html += '<thead><tr>';
  cols.forEach(col => {
    html += `<th>${escapeHtml(col.label)}</th>`;
  });
  html += '</tr></thead>';

  // データ
  html += '<tbody>';
  data.forEach(item => {
    html += '<tr>';
    cols.forEach(col => {
      const value = item[col.key];
      html += `<td>${escapeHtml(String(value ?? ''))}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table></body></html>';

  downloadFile(html, `${filename}.xls`, 'application/vnd.ms-excel');
}

/**
 * ファイルダウンロード
 */
function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * HTMLエスケープ
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, char => map[char]);
}

/**
 * エクスポートボタンコンポーネント用のユーティリティ
 */
export interface ExportButtonProps<T> {
  data: T[];
  filename: string;
  format: ExportFormat;
  columns?: { key: keyof T; label: string }[];
  onExport?: () => void;
}

export function handleExport<T extends Record<string, any>>({
  data,
  filename,
  format,
  columns,
  onExport
}: ExportButtonProps<T>) {
  // タイムスタンプ付きファイル名
  const timestamp = new Date().toISOString().slice(0, 10);
  const fullFilename = `${filename}_${timestamp}`;

  switch (format) {
    case 'csv':
      exportToCSV(data, fullFilename, columns);
      break;
    case 'json':
      exportToJSON(data, fullFilename);
      break;
    case 'excel':
      exportToExcel(data, fullFilename, columns);
      break;
  }

  onExport?.();
}
