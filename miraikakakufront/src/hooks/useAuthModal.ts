'use client';

import { useState, useCallback } from 'react';

type TriggerType = 'watchlist' | 'alert' | 'portfolio' | 'advanced_analysis' | 'export' | 'ai_insights';

interface UseAuthModalReturn {
  isModalOpen: boolean;
  trigger: TriggerType;
  currentAction: string;
  openRegistrationModal: (trigger: TriggerType, currentAction?: string) => void;
  closeModal: () => void;
}

export function useAuthModal(): UseAuthModalReturn {
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

  return {
    isModalOpen,
    trigger,
    currentAction,
    openRegistrationModal,
    closeModal,
  };
}

export function requireAuth<T extends any[]>(
  callback: (...args: T) => void,
  openModal: (trigger: TriggerType, currentAction?: string) => void,
  triggerType: TriggerType
) {
  return (...args: T) => {
    const isAuthenticated = false;
    
    if (!isAuthenticated) {
      openModal(triggerType, window.location.pathname + window.location.search);
      return;
    }
    
    callback(...args);
  };
}