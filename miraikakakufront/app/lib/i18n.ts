import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Translation files
import commonJA from '../../public/locales/ja/common.json';
import commonEN from '../../public/locales/en/common.json';

const resources = {
  ja: {
    common: commonJA
  },
  en: {
    common: commonEN
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'ja', // default language
    fallbackLng: 'ja',
    ns: ['common'], // Explicitly set namespaces
    defaultNS: 'common',
    interpolation: {
      escapeValue: false
    },
    debug: process.env.NODE_ENV === 'development',
    // Force synchronous loading
    initImmediate: false
  });
export default i18n;