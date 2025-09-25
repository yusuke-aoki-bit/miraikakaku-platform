'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Download,
  Filter,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Eye,
  AlertCircle
} from 'lucide-react';

/**
 * Phase 3.3 - Compliance Management Dashboard
 * コンプライアンス管理ダッシュボード
 *
 * Features:
 * - Real-time compliance monitoring
 * - MiFID II / Dodd-Frank violation tracking
 * - Regulatory reporting
 * - Risk-based alerting
 */

interface ComplianceOverview {
  overall_compliance_rate: number;
  total_transactions_30_days: number;
  active_violations: number;
  recent_violations_30_days: number;
}

interface RegimeBreakdown {
  [key: string]: {
    records: number;
    violations: number;
  };
}

interface SeverityBreakdown {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

interface TopViolation {
  rule_id: string;
  regime: string;
  severity: string;
  description: string;
  detected_at: string;
}

interface ComplianceDashboardData {
  compliance_overview: ComplianceOverview;
  regime_breakdown: RegimeBreakdown;
  severity_breakdown: SeverityBreakdown;
  top_violations: TopViolation[];
}

interface ComplianceViolation {
  id: string;
  regime: string;
  rule_id: string;
  severity: string;
  description: string;
  detected_at: string;
  user_id?: string;
  transaction_id?: string;
  remediation_required: boolean;
  resolved: boolean;
  resolved_at?: string;
  resolution_notes?: string;
}

const ComplianceDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<ComplianceDashboardData | null>(null);
  const [violations, setViolations] = useState<ComplianceViolation[]>([]);
  const [loading, setLoading] = useState(true);
  const [violationsLoading, setViolationsLoading] = useState(false);
  const [selectedRegime, setSelectedRegime] = useState<string>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [showResolved, setShowResolved] = useState(false);

  useEffect(() => {
    loadDashboardData();
    loadViolations();
  }, []);

  useEffect(() => {
    loadViolations();
  }, [selectedRegime, selectedSeverity, showResolved]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/compliance/dashboard');
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Error loading compliance dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadViolations = async () => {
    try {
      setViolationsLoading(true);
      const params = new URLSearchParams({
        limit: '20',
        offset: '0'
      });

      if (selectedRegime !== 'all') {
        params.append('regime', selectedRegime);
      }
      if (selectedSeverity !== 'all') {
        params.append('severity', selectedSeverity);
      }
      if (showResolved !== null) {
        params.append('resolved', (!showResolved).toString());
      }

      const response = await fetch(`/api/v1/compliance/violations?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setViolations(data.violations);
      }
    } catch (error) {
      console.error('Error loading violations:', error);
    } finally {
      setViolationsLoading(false);
    }
  };

  const resolveViolation = async (violationId: string, notes: string) => {
    try {
      const response = await fetch(`/api/v1/compliance/violations/${violationId}/resolve`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ resolution_notes: notes })
      });

      if (response.ok) {
        // Reload violations
        loadViolations();
        loadDashboardData();
      }
    } catch (error) {
      console.error('Error resolving violation:', error);
    }
  };

  const generateReport = async (regime: string) => {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 30);

      const response = await fetch('/api/v1/compliance/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          regime: regime,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        })
      });

      if (response.ok) {
        const report = await response.json();

        // Download as JSON file
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `compliance-report-${regime}-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error generating report:', error);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case 'medium':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'low':
        return <Eye className="h-4 w-4 text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRegimeDisplayName = (regime: string) => {
    switch (regime) {
      case 'mifid_ii':
        return 'MiFID II';
      case 'dodd_frank':
        return 'Dodd-Frank';
      case 'cftc':
        return 'CFTC';
      case 'sec':
        return 'SEC';
      case 'esma':
        return 'ESMA';
      default:
        return regime.toUpperCase();
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2 text-lg">読み込み中...</span>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <p className="text-lg">コンプライアンスデータを読み込めませんでした</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center">
            <Shield className="h-8 w-8 text-blue-600 mr-3" />
            コンプライアンス管理
          </h1>
          <p className="text-gray-600 mt-1">
            MiFID II / Dodd-Frank規制遵守監視システム
          </p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={loadDashboardData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            更新
          </Button>
          <Button
            onClick={() => generateReport('mifid_ii')}
            variant="outline"
            size="sm"
          >
            <Download className="h-4 w-4 mr-2" />
            MiFID IIレポート
          </Button>
          <Button
            onClick={() => generateReport('dodd_frank')}
            variant="outline"
            size="sm"
          >
            <Download className="h-4 w-4 mr-2" />
            Dodd-Frankレポート
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <TrendingUp className="h-4 w-4 mr-2 text-green-500" />
              遵守率
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {dashboardData.compliance_overview.overall_compliance_rate}%
            </div>
            <p className="text-xs text-gray-500">過去30日間</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <BarChart3 className="h-4 w-4 mr-2 text-blue-500" />
              取引数
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dashboardData.compliance_overview.total_transactions_30_days.toLocaleString()}
            </div>
            <p className="text-xs text-gray-500">過去30日間</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <AlertTriangle className="h-4 w-4 mr-2 text-red-500" />
              アクティブ違反
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {dashboardData.compliance_overview.active_violations}
            </div>
            <p className="text-xs text-gray-500">要対応</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <Clock className="h-4 w-4 mr-2 text-orange-500" />
              最近の違反
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {dashboardData.compliance_overview.recent_violations_30_days}
            </div>
            <p className="text-xs text-gray-500">過去30日間</p>
          </CardContent>
        </Card>
      </div>

      {/* Regime Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            規制別内訳
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {Object.entries(dashboardData.regime_breakdown).map(([regime, data]) => (
              <div key={regime} className="text-center p-4 border rounded-lg">
                <div className="font-semibold text-lg">
                  {getRegimeDisplayName(regime)}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  取引: {data.records}
                </div>
                <div className={`text-sm mt-1 ${data.violations > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  違反: {data.violations}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Severity Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2" />
            重要度別違反
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(dashboardData.severity_breakdown).map(([severity, count]) => (
              <div key={severity} className="text-center">
                <div className={`inline-flex items-center px-3 py-2 rounded-full ${getSeverityColor(severity)}`}>
                  {getSeverityIcon(severity)}
                  <span className="ml-2 font-semibold">{count}</span>
                </div>
                <div className="text-sm text-gray-600 mt-2 capitalize">
                  {severity === 'critical' ? '緊急' :
                   severity === 'high' ? '高' :
                   severity === 'medium' ? '中' :
                   severity === 'low' ? '低' : severity}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Violations List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <XCircle className="h-5 w-5 mr-2 text-red-500" />
              コンプライアンス違反
            </CardTitle>
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <select
                value={selectedRegime}
                onChange={(e) => setSelectedRegime(e.target.value)}
                className="border rounded px-2 py-1 text-sm"
              >
                <option value="all">全規制</option>
                <option value="mifid_ii">MiFID II</option>
                <option value="dodd_frank">Dodd-Frank</option>
                <option value="cftc">CFTC</option>
                <option value="sec">SEC</option>
              </select>
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="border rounded px-2 py-1 text-sm"
              >
                <option value="all">全重要度</option>
                <option value="critical">緊急</option>
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
              <label className="flex items-center text-sm">
                <input
                  type="checkbox"
                  checked={showResolved}
                  onChange={(e) => setShowResolved(e.target.checked)}
                  className="mr-2"
                />
                解決済みを含む
              </label>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {violationsLoading ? (
            <div className="text-center py-4">
              <RefreshCw className="h-6 w-6 animate-spin mx-auto text-blue-500" />
            </div>
          ) : violations.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <p className="text-lg">違反は見つかりませんでした</p>
            </div>
          ) : (
            <div className="space-y-4">
              {violations.map((violation) => (
                <div
                  key={violation.id}
                  className={`border rounded-lg p-4 ${
                    violation.resolved
                      ? 'bg-green-50 border-green-200'
                      : violation.severity === 'critical'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-white border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getSeverityIcon(violation.severity)}
                      <Badge className={getSeverityColor(violation.severity)}>
                        {violation.severity}
                      </Badge>
                      <Badge variant="outline">
                        {getRegimeDisplayName(violation.regime)}
                      </Badge>
                      {violation.resolved && (
                        <Badge className="bg-green-100 text-green-800">
                          解決済み
                        </Badge>
                      )}
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(violation.detected_at).toLocaleString()}
                    </span>
                  </div>

                  <div className="mb-2">
                    <div className="font-semibold text-gray-900">
                      {violation.rule_id}
                    </div>
                    <div className="text-gray-600 text-sm mt-1">
                      {violation.description}
                    </div>
                  </div>

                  {violation.transaction_id && (
                    <div className="text-xs text-gray-500 mb-2">
                      取引ID: {violation.transaction_id}
                    </div>
                  )}

                  {violation.resolved ? (
                    <div className="text-sm text-green-600">
                      <div>解決日時: {new Date(violation.resolved_at!).toLocaleString()}</div>
                      {violation.resolution_notes && (
                        <div className="mt-1">解決メモ: {violation.resolution_notes}</div>
                      )}
                    </div>
                  ) : (
                    violation.remediation_required && (
                      <Button
                        size="sm"
                        onClick={() => {
                          const notes = prompt('解決メモを入力してください:');
                          if (notes) {
                            resolveViolation(violation.id, notes);
                          }
                        }}
                        className="mt-2"
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        解決としてマーク
                      </Button>
                    )
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ComplianceDashboard;