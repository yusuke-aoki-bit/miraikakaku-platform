'use client';

import { ArrowLeft, Mail, Phone, MapPin, Clock, Send } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function ContactPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    category: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // フォーム送信のシミュレーション（実際はAPIエンドポイントに送信）
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
      setFormData({
        name: '',
        email: '',
        category: '',
        subject: '',
        message: ''
      });
    }, 1000);
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto p-4 md:p-8">
          <button
            onClick={() => router.push('/')}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-8 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            ホームに戻る
          </button>

          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Send className="w-8 h-8 text-green-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">お問い合わせを承りました</h1>
            <p className="text-gray-600 mb-6">
              この度は、お問い合わせいただきありがとうございます。<br />
              内容を確認の上、2-3営業日以内にご返信いたします。
            </p>
            <button
              onClick={() => setSubmitted(false)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors mr-4"
            >
              新しいお問い合わせ
            </button>
            <button
              onClick={() => router.push('/')}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              ホームに戻る
            </button>
          </div>
        </div>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold text-gray-900 mb-4">お問い合わせ</h1>
          <p className="text-gray-600">
            ご質問、ご意見、ご要望などございましたら、お気軽にお問い合わせください。
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Contact Form */}
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">お問い合わせフォーム</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  お名前 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="山田 太郎"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  メールアドレス <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="example@email.com"
                />
              </div>

              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                  お問い合わせ種別 <span className="text-red-500">*</span>
                </label>
                <select
                  id="category"
                  name="category"
                  required
                  value={formData.category}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">選択してください</option>
                  <option value="service">サービスについて</option>
                  <option value="technical">技術的な問題</option>
                  <option value="billing">料金について</option>
                  <option value="partnership">提携について</option>
                  <option value="media">メディア掲載</option>
                  <option value="other">その他</option>
                </select>
              </div>

              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                  件名 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="subject"
                  name="subject"
                  required
                  value={formData.subject}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="お問い合わせの件名"
                />
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                  メッセージ <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="message"
                  name="message"
                  required
                  rows={6}
                  value={formData.message}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="お問い合わせ内容を詳しくお書きください"
                />
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-700">
                  <span className="font-semibold">ご注意：</span>
                  このフォームは投資助言を求めるものではありません。
                  個別銘柄に関する投資判断については、金融のプロフェッショナルにご相談ください。
                </p>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className={`w-full py-3 px-6 rounded-lg font-medium transition-colors ${
                  isSubmitting 
                    ? 'bg-gray-400 text-white cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isSubmitting ? '送信中...' : 'お問い合わせを送信'}
              </button>
            </form>
          </div>

          {/* Contact Information */}
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">連絡先情報</h2>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <Mail className="w-5 h-5 text-blue-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900">メールアドレス</h3>
                    <p className="text-gray-700">info@miraikakaku.com</p>
                    <p className="text-sm text-gray-500">24時間受付</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <Phone className="w-5 h-5 text-blue-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900">電話番号</h3>
                    <p className="text-gray-700">03-1234-5678</p>
                    <p className="text-sm text-gray-500">平日 9:00-18:00</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <MapPin className="w-5 h-5 text-blue-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900">所在地</h3>
                    <p className="text-gray-700">
                      〒100-0001<br />
                      東京都千代田区千代田1-1-1<br />
                      未来ビル10F
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <Clock className="w-5 h-5 text-blue-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900">営業時間</h3>
                    <p className="text-gray-700">
                      月曜日 - 金曜日：9:00 - 18:00<br />
                      土日祝日：休業
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">よくあるご質問</h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Q. サービスの利用料金は？</h3>
                  <p className="text-gray-700 text-sm">
                    基本的な株価予測機能は無料でご利用いただけます。
                    詳細な分析機能については有料プランをご用意しております。
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Q. 予測の精度はどの程度？</h3>
                  <p className="text-gray-700 text-sm">
                    過去のデータに基づく検証では、短期予測で約70-80%の精度を達成しています。
                    ただし、将来の市場動向を保証するものではありません。
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Q. 投資アドバイスはもらえる？</h3>
                  <p className="text-gray-700 text-sm">
                    当サービスは投資判断の参考情報を提供するものであり、
                    具体的な投資アドバイスは行っておりません。
                  </p>
                </div>
              </div>
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