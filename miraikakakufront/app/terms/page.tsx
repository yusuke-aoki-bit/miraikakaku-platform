'use client';

import { useRouter } from 'next/navigation';

export default function TermsPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => router.push('/')}
          className="text-blue-600 dark:text-blue-400 hover:underline mb-4"
        >
          ← ホームに戻る
        </button>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
            利用規約
          </h1>

          <div className="prose dark:prose-invert max-w-none">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              最終更新日: 2025年10月3日
            </p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                第1条（適用）
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                本規約は、Miraikakaku（以下「当サービス」といいます）の利用に関する条件を、当サービスを利用するすべてのユーザー（以下「ユーザー」といいます）と当サービス運営者（以下「当社」といいます）との間で定めるものです。
              </p>
              <p className="text-gray-700 dark:text-gray-300">
                ユーザーは、当サービスを利用することにより、本規約に同意したものとみなされます。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                第2条（サービスの内容）
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                当サービスは、AI技術を用いた株価予測情報を提供するプラットフォームです。
              </p>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                提供する情報には以下が含まれます：
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-4 space-y-2">
                <li>株価の予測データ</li>
                <li>市場データおよび統計情報</li>
                <li>銘柄情報および分析ツール</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                第3条（免責事項）
              </h2>
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 p-4 mb-4">
                <p className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                  重要: 投資助言ではありません
                </p>
                <p className="text-gray-700 dark:text-gray-300">
                  当サービスが提供する情報は、投資の助言や推奨を目的としたものではありません。
                  すべての投資判断は、ユーザー自身の責任において行ってください。
                </p>
              </div>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                当社は、以下について一切の責任を負いません：
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-4 space-y-2">
                <li>当サービスの予測情報の正確性、完全性、有用性</li>
                <li>当サービスの利用によって生じた損害または損失</li>
                <li>投資判断の結果として発生した損益</li>
                <li>当サービスの中断、停止、終了によって生じた損害</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                第4条（禁止事項）
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                ユーザーは、当サービスの利用にあたり、以下の行為を行ってはなりません：
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2">
                <li>法令または公序良俗に違反する行為</li>
                <li>当サービスの運営を妨害する行為</li>
                <li>他のユーザーまたは第三者の権利を侵害する行為</li>
                <li>不正アクセスまたはそれに類する行為</li>
                <li>当サービスのデータを無断で複製、転載、配布する行為</li>
                <li>商用目的での無断利用</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                第5条（知的財産権）
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                当サービスに関する知的財産権は、すべて当社または正当な権利者に帰属します。
                ユーザーは、当サービスの情報を私的使用の範囲を超えて利用することはできません。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                第6条（サービスの変更・停止）
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                当社は、ユーザーへの事前の通知なく、当サービスの内容を変更、または提供を中断・終了することができるものとします。
                これによってユーザーに生じた損害について、当社は一切の責任を負いません。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                第7条（規約の変更）
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                当社は、必要に応じて本規約を変更することができるものとします。
                変更後の規約は、当サービス上に掲載した時点から効力を生じるものとします。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                第8条（準拠法および管轄裁判所）
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                本規約の準拠法は日本法とします。
              </p>
              <p className="text-gray-700 dark:text-gray-300">
                当サービスに関する一切の紛争については、東京地方裁判所を第一審の専属的合意管轄裁判所とします。
              </p>
            </section>

            <div className="mt-12 pt-6 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                ご質問やご不明な点がございましたら、お問い合わせください。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
