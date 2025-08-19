'use client';

import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react';
import { useToast } from '@/hooks/useToast';

interface ToastProps {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number; // in ms
}

const icons = {
  success: <CheckCircle className="w-5 h-5 text-green-400" />,
  error: <XCircle className="w-5 h-5 text-red-400" />,
  info: <Info className="w-5 h-5 text-blue-400" />,
  warning: <AlertTriangle className="w-5 h-5 text-yellow-400" />,
};

const Toast: React.FC<ToastProps> = ({ id, message, type, duration = 5000 }) => {
  const { removeToast } = useToast();

  useEffect(() => {
    const timer = setTimeout(() => {
      removeToast(id);
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, id, removeToast]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 50, scale: 0.3 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.5 }}
      className={`flex items-center gap-x-3 p-4 rounded-lg shadow-lg text-text-light border border-dark-border backdrop-blur-md
        ${type === 'success' ? 'bg-green-900/50' : ''}
        ${type === 'error' ? 'bg-brand-primary/50' : ''}
        ${type === 'info' ? 'bg-blue-900/50' : ''}
        ${type === 'warning' ? 'bg-yellow-900/50' : ''}
      `}
    >
      {icons[type]}
      <span className="flex-1 text-sm font-medium">{message}</span>
      <button onClick={() => removeToast(id)} className="text-text-medium hover:text-text-light">
        <X className="w-4 h-4" />
      </button>
    </motion.div>
  );
};

export const ToastContainer: React.FC = () => {
  const { toasts } = useToast();

  return (
    <div className="fixed bottom-layout-gap right-layout-gap z-[9999] flex flex-col gap-y-3 pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} />
        ))}
      </AnimatePresence>
    </div>
  );
};
