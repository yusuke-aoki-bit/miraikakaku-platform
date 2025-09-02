'use client';

import { ArrowLeft, Building, Mail, Globe, Users, Target, Lightbulb } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function AboutPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-4 md:p-8">
        {/* Navigation */}
        <button
          onClick={() => router.push('/')}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          ホームに戻る
        </button>

        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">会社概要</h1>
          <p className="text-gray-600">
            AI技術で投資の未来を切り拓く
          </p>
        </div>

        {/* Company Information */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">会社情報</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="flex items-start space-x-3">
                <Building className="w-5 h-5 text-blue-600 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900">会社名</h3>
                  <p className="text-gray-700">株式会社 未来価格</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <Globe className="w-5 h-5 text-blue-600 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900">設立年月日</h3>
                  <p className="text-gray-700">2023年1月1日</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Users className="w-5 h-5 text-blue-600 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900">代表取締役</h3>
                  <p className="text-gray-700">山田 太郎</p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div className="flex items-start space-x-3">
                <Building className="w-5 h-5 text-blue-600 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900">本社所在地</h3>
                  <p className="text-gray-700">
                    〒100-0001<br />
                    東京都千代田区千代田1-1-1<br />
                    未来ビル10F
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Mail className="w-5 h-5 text-blue-600 mt-1" />
                <div>
                  <h3 className="font-semibold text-gray-900">お問い合わせ</h3>
                  <p className="text-gray-700">info@miraikakaku.com</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Mission */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center mb-6">
            <Target className="w-6 h-6 text-blue-600 mr-3" />
            <h2 className="text-2xl font-semibold text-gray-900">ミッション</h2>
          </div>
          <p className="text-gray-700 text-lg leading-relaxed">
            私たちは、最先端のAI技術を活用して株価予測の精度を向上させ、
            すべての投資家がより良い投資判断を行えるよう支援することを使命としています。
            データサイエンスの力で金融市場の透明性を高め、
            より公平で効率的な投資環境の実現を目指します。
          </p>
        </div>

        {/* Vision */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center mb-6">
            <Lightbulb className="w-6 h-6 text-blue-600 mr-3" />
            <h2 className="text-2xl font-semibold text-gray-900">ビジョン</h2>
          </div>
          <p className="text-gray-700 text-lg leading-relaxed">
            AI技術により予測される「未来価格」を通じて、
            投資家の皆様が自信を持って投資判断を行える世界を創造します。
            私たちのプラットフォームが、投資の民主化と金融リテラシーの向上に貢献し、
            すべての人が豊かな未来を築けるよう支援していきます。
          </p>
        </div>

        {/* Services */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">事業内容</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="p-6 bg-blue-50 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">AI株価予測サービス</h3>
              <p className="text-blue-800">
                LSTM（Long Short-Term Memory）ニューラルネットワークを用いた
                高精度な株価予測システムの提供
              </p>
            </div>
            
            <div className="p-6 bg-green-50 rounded-lg">
              <h3 className="text-lg font-semibold text-green-900 mb-3">データ分析・可視化</h3>
              <p className="text-green-800">
                複雑な金融データを分かりやすいチャートや
                グラフで可視化するツールの開発・提供
              </p>
            </div>
            
            <div className="p-6 bg-purple-50 rounded-lg">
              <h3 className="text-lg font-semibold text-purple-900 mb-3">投資支援システム</h3>
              <p className="text-purple-800">
                個人投資家から機関投資家まで、
                様々なニーズに対応した投資意思決定支援システム
              </p>
            </div>
            
            <div className="p-6 bg-orange-50 rounded-lg">
              <h3 className="text-lg font-semibold text-orange-900 mb-3">金融教育コンテンツ</h3>
              <p className="text-orange-800">
                投資初心者から上級者まで学べる
                金融リテラシー向上のための教育プログラム
              </p>
            </div>
          </div>
        </div>

        {/* Values */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">私たちの価値観</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">🎯 精度への追求</h3>
              <p className="text-gray-700">
                常に最新の技術と手法を研究し、予測精度の向上に妥協しません。
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">🤝 透明性の重視</h3>
              <p className="text-gray-700">
                AI の判断根拠を可能な限り可視化し、ユーザーが理解できる形で提供します。
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">🌟 イノベーション</h3>
              <p className="text-gray-700">
                既存の枠にとらわれず、新しいアイデアと技術で金融業界に革新をもたらします。
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">🛡️ 責任ある運営</h3>
              <p className="text-gray-700">
                投資リスクを適切に伝え、ユーザーの資産形成を責任を持って支援します。
              </p>
            </div>
          </div>
        </div>

        {/* History */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">沿革</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="w-20 flex-shrink-0 text-sm font-semibold text-blue-600">2023年1月</div>
              <p className="text-gray-700">株式会社未来価格設立</p>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="w-20 flex-shrink-0 text-sm font-semibold text-blue-600">2023年3月</div>
              <p className="text-gray-700">AI株価予測システムのプロトタイプ開発開始</p>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="w-20 flex-shrink-0 text-sm font-semibold text-blue-600">2023年7月</div>
              <p className="text-gray-700">ベータ版サービス「未来価格」リリース</p>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="w-20 flex-shrink-0 text-sm font-semibold text-blue-600">2023年12月</div>
              <p className="text-gray-700">正式サービス開始、ユーザー数1万人突破</p>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="w-20 flex-shrink-0 text-sm font-semibold text-blue-600">2024年1月</div>
              <p className="text-gray-700">現在に至る</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>© 2024 未来価格. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}