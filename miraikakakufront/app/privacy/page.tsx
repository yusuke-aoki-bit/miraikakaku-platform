'use client';

import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function PrivacyPolicyPage() {
  const router = useRouter(
  return (
    <div className="min-h-screen bg-content-bg">
      <div className="max-w-4xl mx-auto p-4 md:p-8">
        {/* Navigation */}
        <button
          onClick={() => router.push('/')}
          className="flex items-center text-primary hover:text-primary-hover mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          ホームに戻る
        </button>

        {/* Header */}
        <div className="bg-surface rounded-lg shadow-md p-8 mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-4">プライバシーポリシー</h1>
          <p className="text-text-secondary">
            最終更新日：2024年1月1日
          </p>
        </div>

        {/* Content */}
        <div className="bg-surface rounded-lg shadow-md p-8 space-y-8">
          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">1. 個人情報の収集</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                未来価格（以下「当サービス」）では、サービスの提供および改善のために、以下の個人情報を収集する場合があります。
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>メールアドレス</li>
                <li>ユーザー名</li>
                <li>サービス利用履歴</li>
                <li>アクセスログ</li>
                <li>Cookie情報</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">2. 個人情報の利用目的</h2>
            <div className="prose text-content-text space-y-4">
              <p>収集した個人情報は、以下の目的で利用いたします。</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>サービスの提供・運営</li>
                <li>ユーザーサポートの提供</li>
                <li>サービスの改善・新機能の開発</li>
                <li>利用状況の分析</li>
                <li>重要なお知らせの配信</li>
                <li>不正利用の防止</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">3. 個人情報の第三者提供</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                当サービスは、法令に基づく場合を除き、ユーザーの同意なしに個人情報を第三者に提供することはありません。
              </p>
              <p>ただし、以下の場合は例外とします。</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>法令に基づく開示要求がある場合</li>
                <li>ユーザーまたは第三者の生命、身体、財産等を保護するために必要な場合</li>
                <li>サービス提供のために必要な業務委託先への提供</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">4. Cookie について</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                当サービスでは、ユーザーエクスペリエンスの向上のためにCookieを使用しています。
              </p>
              <p>
                Cookieの使用を無効にすることも可能ですが、その場合、サービスの一部機能がご利用いただけない場合があります。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">5. データの保管・セキュリティ</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                当サービスは、収集した個人情報の安全性を確保するため、適切なセキュリティ対策を実施しています。
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>SSL/TLS暗号化による通信の保護</li>
                <li>アクセス制限による不正アクセスの防止</li>
                <li>定期的なセキュリティ監査の実施</li>
                <li>従業員への個人情報保護教育の実施</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">6. ユーザーの権利</h2>
            <div className="prose text-content-text space-y-4">
              <p>ユーザーは、自身の個人情報について以下の権利を有します。</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>個人情報の開示請求</li>
                <li>個人情報の訂正・追加・削除</li>
                <li>個人情報の利用停止・消去</li>
                <li>個人情報の第三者提供の停止</li>
              </ul>
              <p>
                これらの権利行使をご希望の場合は、お問い合わせフォームからご連絡ください。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">7. 本ポリシーの変更</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                当サービスは、法令の変更や事業内容の変更等により、本プライバシーポリシーを変更する場合があります。
              </p>
              <p>
                重要な変更については、サービス内での通知またはメールにてお知らせいたします。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">8. お問い合わせ</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                本プライバシーポリシーに関するお問い合わせは、以下までご連絡ください。
              </p>
              <div className="bg-surface-variant p-4 rounded-lg">
                <p className="font-semibold">未来価格 サポートチーム</p>
                <p>メール：privacy@miraikakaku.com</p>
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-content-text-secondary text-sm">
          <p>© 2024 未来価格. All rights reserved.</p>
        </div>
      </div>
    </div>
}