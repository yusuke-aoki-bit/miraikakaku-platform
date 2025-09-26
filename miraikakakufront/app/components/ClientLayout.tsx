'use client';

import { I18nextProvider } from "react-i18next";
import i18n from "../lib/i18n";

export default function ClientLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <I18nextProvider i18n={i18n}>
      {children}
    </I18nextProvider>
  );
}