'use client';

import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

export default function TermsOfServicePage() {
  const router = useRouter(
  const { t } = useTranslation('common'
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
          {t('navigation.backToHome', 'ホームに戻る')}
        </button>

        {/* Header */}
        <div className="rounded-lg shadow-md p-8 mb-8" style={{
          backgroundColor: 'var(--yt-music-surface)'
          border: '1px solid var(--yt-music-border)'
        }}>
          <h1 className="text-3xl font-bold mb-4" style={{ color: 'var(--yt-music-text-primary)' }}>{t('terms.title', '利用規約')}</h1>
          <p style={{ color: 'var(--yt-music-text-secondary)' }}>
            {t('terms.lastUpdated', '最終更新日：2024年1月1日')}
          </p>
        </div>

        {/* Content */}
        <div className="rounded-lg shadow-md p-8 space-y-8" style={{
          backgroundColor: 'var(--yt-music-surface)'
          border: '1px solid var(--yt-music-border)'
        }}>
          <section>
            <h2 className="text-2xl font-semibold mb-4" style={{ color: 'var(--yt-music-text-primary)' }}>第1条（適用）</h2>
            <div className="prose space-y-4" style={{ color: 'var(--yt-music-text-secondary)' }}>
              <p>
                この利用規約（以下「本規約」）は、未来価格（以下「当社」）が提供するサービス「未来価格」（以下「本サービス」）の利用条件を定めるものです。
              </p>
              <p>
                登録ユーザーの皆さま（以下「ユーザー」）には、本規約に従って本サービスをご利用いただきます。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第2条（利用登録）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                登録希望者は、本規約に同意の上、当社の定める方法によって利用登録を申請するものとします。
              </p>
              <p>
                当社は、利用登録の申請者に以下の事由があると判断した場合、利用登録の申請を承認しないことがあります。
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>利用登録の申請に際して虚偽の事項を届け出た場合</li>
                <li>本規約に違反したことがある者からの申請である場合</li>
                <li>その他、当社が利用登録を相当でないと判断した場合</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第3条（ユーザーIDおよびパスワードの管理）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                ユーザーは、自己の責任において、本サービスのユーザーIDおよびパスワードを適切に管理するものとします。
              </p>
              <p>
                ユーザーは、いかなる場合にも、ユーザーIDおよびパスワードを第三者に譲渡または貸与し、もしくは第三者と共用することはできません。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第4条（禁止事項）</h2>
            <div className="prose text-content-text space-y-4">
              <p>ユーザーは、本サービスの利用にあたり、以下の行為をしてはなりません。</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>法令または公序良俗に違反する行為</li>
                <li>犯罪行為に関連する行為</li>
                <li>本サービスの内容等、本サービスに含まれる著作権、商標権その他の知的財産権を侵害する行為</li>
                <li>当社、ほかのユーザー、またはその他第三者のサーバーまたはネットワークの機能を破壊したり、妨害したりする行為</li>
                <li>本サービスによって得られた情報を商業的に利用する行為</li>
                <li>当社のサービスの運営を妨害するおそれのある行為</li>
                <li>不正アクセスをし、またはこれを試みる行為</li>
                <li>他のユーザーに関する個人情報等を収集または蓄積する行為</li>
                <li>不正な目的を持って本サービスを利用する行為</li>
                <li>本サービスの他のユーザーまたはその他の第三者に不利益、損害、不快感を与える行為</li>
                <li>その他、当社が不適切と判断する行為</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第5条（本サービスの提供の停止等）</h2>
            <div className="prose text-content-text space-y-4">
              <p>当社は、以下のいずれかの事由があると判断した場合、ユーザーに事前に通知することなく本サービスの全部または一部の提供を停止または中断することができるものとします。</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>本サービスにかかるコンピュータシステムの保守点検または更新を行う場合</li>
                <li>地震、落雷、火災、停電または天災などの不可抗力により、本サービスの提供が困難となった場合</li>
                <li>コンピュータまたは通信回線等が事故により停止した場合</li>
                <li>その他、当社が本サービスの提供が困難と判断した場合</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第6条（著作権）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                ユーザーは、自ら著作権等の必要な知的財産権を有するか、または必要な権利者の許諾を得た文章、画像や映像等の情報に関してのみ、本サービスを利用し、投稿ないしアップロードすることができるものとします。
              </p>
              <p>
                本サービスに関して当社が作成した著作物に関する著作権その他の知的財産権については、当社に帰属するものとします。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第7条（利用制限および登録抹消）</h2>
            <div className="prose text-content-text space-y-4">
              <p>当社は、ユーザーが以下のいずれかに該当する場合には、事前の通知なく、投稿データを削除し、ユーザーに対して本サービスの全部もしくは一部の利用を制限し、またはユーザーとしての登録を抹消することができるものとします。</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>本規約のいずれかの条項に違反した場合</li>
                <li>登録事項に虚偽の事実があることが判明した場合</li>
                <li>当社からの連絡に対し、一定期間返答がない場合</li>
                <li>本サービスについて、最終の利用から一定期間利用がない場合</li>
                <li>その他、当社が本サービスの利用を適当でないと判断した場合</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第8条（免責事項）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                当社は、本サービスに事実上または法律上の瑕疵（安全性、信頼性、正確性、完全性、有効性、特定の目的への適合性、セキュリティなどに関する欠陥、エラーやバグ、権利侵害などを含みます。）がないことを明示的にも黙示的にも保証しておりません。
              </p>
              <p>
                当社は、本サービスに起因してユーザーに生じたあらゆる損害について、当社の故意または重過失による場合を除き、一切の責任を負いません。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第9条（サービス内容の変更等）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                当社は、ユーザーへの事前の告知をもって、本サービスの内容を変更、追加または廃止することがあり、ユーザーはこれを承諾するものとします。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第10条（利用規約の変更）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                当社は以下の場合には、ユーザーの個別の同意を要せず、本規約を変更することができるものとします。
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>本規約の変更がユーザーの一般の利益に適合するとき。</li>
                <li>本規約の変更が本サービス利用契約の目的に反せず、かつ、変更の必要性、変更後の内容の相当性その他の変更に係る事情に照らして合理的なものであるとき。</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第11条（個人情報の取扱い）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                当社は、本サービスの利用によって取得する個人情報については、当社「プライバシーポリシー」に従い適切に取り扱うものとします。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第12条（通知または連絡）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                ユーザーと当社との間の通知または連絡は、当社の定める方法によって行うものとします。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第13条（権利義務の譲渡の禁止）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                ユーザーは、当社の書面による事前の承諾なく、利用契約上の地位または本規約に基づく権利もしくは義務を第三者に譲渡し、または担保に供することはできません。
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-text-primary mb-4">第14条（準拠法・裁判管轄）</h2>
            <div className="prose text-content-text space-y-4">
              <p>
                本規約の解釈にあたっては、日本法を準拠法とします。
              </p>
              <p>
                本サービスに関して紛争が生じた場合には、当社の本店所在地を管轄する裁判所を専属的合意管轄とします。
              </p>
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