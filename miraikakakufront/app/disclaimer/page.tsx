'use client';

import { ArrowLeft, AlertTriangle, Shield, Info, TrendingUp, BookOpen } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function DisclaimerPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--yt-music-bg)' }}>
      <div className="max-w-4xl mx-auto p-4 md:p-8">
        {/* Navigation */}
        <button
          onClick={() => router.push('/')}
          className="flex items-center mb-8 transition-colors"
          style={{ color: 'var(--yt-music-primary)' }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = 'var(--yt-music-accent)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--yt-music-primary)';
          }}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          ホームに戻る
        </button>

        {/* Header */}
        <div className="rounded-lg shadow-md p-8 mb-8" style={{
          backgroundColor: 'var(--yt-music-surface)',
          border: '1px solid var(--yt-music-border)'
        }}>
          <div className="flex items-center mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600 mr-3" />
            <h1 className="text-3xl font-bold" style={{ color: 'var(--yt-music-text-primary)' }}>免責事項</h1>
          </div>
          <p style={{ color: 'var(--yt-music-text-secondary)' }}>
            本サービスをご利用になる前に、必ずお読みください
          </p>
        </div>

        {/* Important Notice */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-red-600 mt-1 flex-shrink-0" />
            <div>
              <h2 className="text-xl font-semibold text-red-900 mb-3">重要な注意事項</h2>
              <p className="text-red-800 leading-relaxed">
                「未来価格」で提供される株価予測および関連する分析情報は、<strong>情報提供のみを目的としており、投資助言や金融アドバイスではありません。</strong>
                投資判断はお客様ご自身の責任において行ってください。
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-8">
          {/* Investment Risk */}
          <div className="rounded-lg shadow-md p-8" style={{
            backgroundColor: 'var(--yt-music-surface)',
            border: '1px solid var(--yt-music-border)'
          }}>
            <div className="flex items-center mb-6">
              <TrendingUp className="w-6 h-6 text-orange-600 mr-3" />
              <h2 className="text-2xl font-semibold" style={{ color: 'var(--yt-music-text-primary)' }}>投資リスクについて</h2>
            </div>
            <div className="prose space-y-4" style={{ color: 'var(--yt-music-text-secondary)' }}>
              <p>
                株式投資には以下のようなリスクが伴います。投資を行う前に十分ご理解ください。
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>価格変動リスク：</strong>株価は経済情勢、企業の業績、市場の需給等により大きく変動する可能性があります</li>
                <li><strong>流動性リスク：</strong>市場の状況によっては売買が困難になる場合があります</li>
                <li><strong>信用リスク：</strong>投資先企業の経営悪化等により損失を被る可能性があります</li>
                <li><strong>為替リスク：</strong>外国株式投資の場合、為替相場の変動により損失を被る可能性があります</li>
                <li><strong>カントリーリスク：</strong>投資対象国の政治・経済情勢の変化による影響を受ける可能性があります</li>
              </ul>
            </div>
          </div>

          {/* AI Prediction Limitations */}
          <div className="rounded-lg shadow-md p-8" style={{
            backgroundColor: 'var(--yt-music-surface)',
            border: '1px solid var(--yt-music-border)'
          }}>
            <div className="flex items-center mb-6">
              <Info className="w-6 h-6 text-blue-600 mr-3" />
              <h2 className="text-2xl font-semibold" style={{ color: 'var(--yt-music-text-primary)' }}>AI予測の限界について</h2>
            </div>
            <div className="prose space-y-4" style={{ color: 'var(--yt-music-text-secondary)' }}>
              <p>
                当サービスで提供するAI株価予測には以下の限界があります。
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>過去データ依存：</strong>予測は過去の価格データに基づいており、未来の市場環境変化を完全に予測することはできません</li>
                <li><strong>予測精度：</strong>予測の精度は100%ではなく、実際の価格動向と異なる場合があります</li>
                <li><strong>突発的事象：</strong>自然災害、戦争、パンデミック等の突発的な事象は予測に反映されていません</li>
                <li><strong>市場構造変化：</strong>市場構造の根本的な変化により予測モデルの有効性が低下する可能性があります</li>
                <li><strong>技術的制約：</strong>AIモデルは定期的に更新されますが、技術的制約により完璧な予測はできません</li>
              </ul>
            </div>
          </div>

          {/* Service Limitations */}
          <div className="rounded-lg shadow-md p-8" style={{
            backgroundColor: 'var(--yt-music-surface)',
            border: '1px solid var(--yt-music-border)'
          }}>
            <div className="flex items-center mb-6">
              <Shield className="w-6 h-6 text-green-600 mr-3" />
              <h2 className="text-2xl font-semibold" style={{ color: 'var(--yt-music-text-primary)' }}>サービス提供に関する免責</h2>
            </div>
            <div className="prose space-y-4" style={{ color: 'var(--yt-music-text-secondary)' }}>
              <p>
                当社は、本サービスに関して以下の点についてお客様にご理解いただきます。
              </p>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>1. 情報の正確性</h3>
                  <p>
                    提供される情報の正確性、完全性、最新性について保証するものではありません。
                    情報の誤りや遅延により生じた損害について責任を負いません。
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>2. サービスの可用性</h3>
                  <p>
                    システムメンテナンス、障害、不可抗力等によりサービスが一時的に利用できない場合があります。
                    これらの理由によるサービス中断について責任を負いません。
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>3. 投資損失</h3>
                  <p>
                    本サービスの利用により生じた投資損失について、いかなる理由があっても責任を負いません。
                    投資はお客様の自己責任において行ってください。
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>4. 第三者への影響</h3>
                  <p>
                    お客様が本サービスを利用することにより第三者に与えた損害について、責任を負いません。
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Legal Compliance */}
          <div className="rounded-lg shadow-md p-8" style={{
            backgroundColor: 'var(--yt-music-surface)',
            border: '1px solid var(--yt-music-border)'
          }}>
            <div className="flex items-center mb-6">
              <BookOpen className="w-6 h-6 text-purple-600 mr-3" />
              <h2 className="text-2xl font-semibold" style={{ color: 'var(--yt-music-text-primary)' }}>法的事項</h2>
            </div>
            <div className="prose space-y-4" style={{ color: 'var(--yt-music-text-secondary)' }}>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>金融商品取引法について</h3>
                  <p>
                    当社は金融商品取引業者ではありません。本サービスは投資助言・代理業に該当するサービスを提供するものではありません。
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>著作権について</h3>
                  <p>
                    本サービスで提供されるコンテンツの著作権は当社または第三者に帰属します。
                    無断での複製、転載、配布等は禁止されています。
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--yt-music-text-primary)' }}>準拠法・裁判管轄</h3>
                  <p>
                    本免責事項および本サービスに関する争いについては、日本法を準拠法とし、
                    東京地方裁判所を専属的合意管轄裁判所とします。
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8">
            <h2 className="text-2xl font-semibold mb-6" style={{ color: 'var(--yt-music-text-primary)' }}>推奨事項</h2>
            <div className="prose space-y-4" style={{ color: 'var(--yt-music-text-secondary)' }}>
              <p className="font-semibold" style={{ color: 'var(--yt-music-text-primary)' }}>
                安全で適切な投資を行うために、以下の点をお勧めします：
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>投資に関する基礎知識を身につける</li>
                <li>複数の情報源から情報を収集し、総合的に判断する</li>
                <li>リスク許容度に応じた適切な投資額を設定する</li>
                <li>分散投資を心がける</li>
                <li>定期的な投資方針の見直しを行う</li>
                <li>必要に応じて専門家（ファイナンシャル・プランナー等）に相談する</li>
              </ul>
            </div>
          </div>

          {/* Update Information */}
          <div className="rounded-lg shadow-md p-8" style={{
            backgroundColor: 'var(--yt-music-surface)',
            border: '1px solid var(--yt-music-border)'
          }}>
            <h2 className="text-2xl font-semibold mb-6" style={{ color: 'var(--yt-music-text-primary)' }}>免責事項の更新</h2>
            <div className="prose space-y-4" style={{ color: 'var(--yt-music-text-secondary)' }}>
              <p>
                本免責事項は予告なく変更される場合があります。
                重要な変更については、サービス内での通知またはメールにてお知らせいたします。
              </p>
              <p className="text-sm" style={{ color: 'var(--yt-music-text-disabled)' }}>
                最終更新日：2024年1月1日
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm" style={{ color: 'var(--yt-music-text-disabled)' }}>
          <p>© 2024 未来価格. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}