/**
 * Safe number formatting utilities
 */

/**
 * Safely format a number with locale string
 * Returns fallback value if input is null, undefined, or NaN
 */
export function safeToLocaleString(
  value: number | null | undefined,
  fallback: string = '-'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  return value.toLocaleString();
}

/**
 * Safely format currency (Yen)
 */
export function formatCurrency(
  value: number | null | undefined,
  fallback: string = '-'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  return `¥${value.toLocaleString()}`;
}

/**
 * Safely format percentage
 */
export function formatPercentage(
  value: number | null | undefined,
  decimals: number = 2,
  fallback: string = '-'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  return `${value.toFixed(decimals)}%`;
}

/**
 * Safely format change with sign
 */
export function formatChange(
  value: number | null | undefined,
  fallback: string = '-'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toLocaleString()}`;
}

/**
 * Safely format currency change with sign
 */
export function formatCurrencyChange(
  value: number | null | undefined,
  fallback: string = '-'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  const sign = value >= 0 ? '+' : '';
  return `${sign}¥${value.toLocaleString()}`;
}

/**
 * Safely format date
 */
export function formatDate(
  date: Date | string | number | null | undefined,
  locale: string = 'ja-JP',
  fallback: string = '-'
): string {
  if (!date) {
    return fallback;
  }

  try {
    const dateObj = typeof date === 'string' || typeof date === 'number'
      ? new Date(date)
      : date;

    if (isNaN(dateObj.getTime())) {
      return fallback;
    }

    return dateObj.toLocaleString(locale);
  } catch (error) {
    console.error('Error formatting date:', error);
    return fallback;
  }
}

/**
 * Check if value is a valid number
 */
export function isValidNumber(value: any): value is number {
  return typeof value === 'number' && !isNaN(value) && isFinite(value);
}

/**
 * Get safe number value with fallback
 */
export function getSafeNumber(
  value: number | null | undefined,
  fallback: number = 0
): number {
  if (value === null || value === undefined || isNaN(value)) {
    return fallback;
  }
  return value;
}

/**
 * Safely format number with toFixed
 * Handles string inputs and null/undefined values
 */
export function safeToFixed(
  value: number | string | null | undefined,
  decimals: number = 2,
  fallback: string = '0.00'
): string {
  if (value === null || value === undefined) {
    return fallback;
  }

  const numValue = typeof value === 'string' ? parseFloat(value) : value;

  if (isNaN(numValue)) {
    return fallback;
  }

  return numValue.toFixed(decimals);
}
