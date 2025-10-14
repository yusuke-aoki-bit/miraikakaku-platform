'use client';

import { useRouter } from 'next/navigation';

export default function PrivacyPage() {
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
            プライバシーポリシー
          </h1>

          <div className="prose dark:prose-invert max-w-none">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              最終更新日: 2025年10月3日
            </p>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                1. 個人情報の収集
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                当サービス（Miraikakaku）では、サービス提供のために以下の情報を収集する場合があります：
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2">
                <li>アクセスログ情報（IPアドレス、ブラウザ情報、アクセス日時等）</li>
                <li>Cookie およびWeb ビーコン情報</li>
                <li>サービス利用状況に関する情報</li>
                <li>ユーザー登録時に提供いただいた情報（将来的に実装予定）</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                2. 個人情報の利用目的
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                収集した個人情報は、以下の目的で利用します：
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2">
                <li>サービスの提供、運営、維持、改善</li>
                <li>ユーザーサポートの提供</li>
                <li>サービスに関する通知、アップデート情報の送信</li>
                <li>利用状況の分析および統計</li>
                <li>不正利用の防止およびセキュリティの向上</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                3. 個人情報の第三者提供
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                当社は、以下の場合を除き、ユーザーの同意なく個人情報を第三者に提供することはありません：
              </p>
              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 space-y-2">
                <li>法令に基づく場合</li>
                <li>人の生命、身体または財産の保護のために必要がある場合</li>
                <li>公衆衛生の向上または児童の健全な育成の推進のために特に必要がある場合</li>
                <li>国の機関もしくは地方公共団体またはその委託を受けた者が法令の定める事務を遂行することに対して協力する必要がある場合</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                4. Cookie（クッキー）の使用
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                当サービスでは、ユーザーエクスペリエンスの向上のためにCookieを使用しています。
              </p>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Cookieとは、Webサイトがユーザーのコンピュータに一時的にデータを書き込んで保存させる仕組みです。
                ユーザーはブラウザの設定でCookieを無効にすることができますが、一部機能が利用できなくなる場合があります。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                5. アクセス解析ツール
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                当サービスでは、サービス向上のためにアクセス解析ツールを使用する場合があります。
                これらのツールはCookieを使用してユーザーの訪問情報を収集しますが、個人を特定する情報は含まれません。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                6. 個人情報の安全管理
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                当社は、個人情報の漏洩、滅失、毀損等を防止するため、適切な安全管理措置を講じます。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                7. 個人情報の開示・訂正・削除
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                ユーザーは、当社が保有する自己の個人情報について、開示、訂正、削除を請求することができます。
                請求方法については、お問い合わせください。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                8. プライバシーポリシーの変更
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                当社は、必要に応じて本プライバシーポリシーを変更することがあります。
                変更後のプライバシーポリシーは、当サービス上に掲載した時点から効力を生じるものとします。
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                9. お問い合わせ
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                本プライバシーポリシーに関するお問い合わせは、以下までご連絡ください：
              </p>
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <p className="text-gray-700 dark:text-gray-300">
                  Miraikakaku 運営チーム<br />
                  Email: privacy@miraikakaku.com（準備中）
                </p>
              </div>
            </section>

            <div className="mt-12 pt-6 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                本プライバシーポリシーは、個人情報保護法に基づいて作成されています。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
