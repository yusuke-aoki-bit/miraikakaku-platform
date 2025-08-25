'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import RegistrationModal from '@/components/auth/RegistrationModal';

type TriggerType = 'watchlist' | 'alert' | 'portfolio' | 'advanced_analysis' | 'export' | 'ai_insights';

interface AuthModalContextType {
  openRegistrationModal: (trigger: TriggerType, currentAction?: string) => void;
  closeModal: () => void;
  requireAuth: <T extends any[]>(
    callback: (...args: T) => void,
    triggerType: TriggerType
  ) => (...args: T) => void;
}

const AuthModalContext = createContext<AuthModalContextType | undefined>(undefined);

interface AuthModalProviderProps {
  children: ReactNode;
}

export function AuthModalProvider({ children }: AuthModalProviderProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [trigger, setTrigger] = useState<TriggerType>('watchlist');
  const [currentAction, setCurrentAction] = useState('');

  const openRegistrationModal = useCallback((triggerType: TriggerType, action?: string) => {
    setTrigger(triggerType);
    setCurrentAction(action || window.location.pathname);
    setIsModalOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
  }, []);

  const requireAuth = useCallback(<T extends any[]>(
    callback: (...args: T) => void,
    triggerType: TriggerType
  ) => {
    return (...args: T) => {
      const isAuthenticated = false;
      
      if (!isAuthenticated) {
        openRegistrationModal(triggerType, window.location.pathname + window.location.search);
        return;
      }
      
      callback(...args);
    };
  }, [openRegistrationModal]);

  const value = {
    openRegistrationModal,
    closeModal,
    requireAuth,
  };

  return (
    <AuthModalContext.Provider value={value}>
      {children}
      <RegistrationModal
        isOpen={isModalOpen}
        onClose={closeModal}
        trigger={trigger}
        currentAction={currentAction}
      />
    </AuthModalContext.Provider>
  );
}

export function useAuthModal() {
  const context = useContext(AuthModalContext);
  if (context === undefined) {
    throw new Error('useAuthModal must be used within an AuthModalProvider');
  }
  return context;
}