import React from 'react';
import { AIPanelContainer } from './ai/AIPanelContainer';
import { User } from '@supabase/supabase-js';

interface AIPanelProps {
  user: User;
  activePageId?: string;
  activePageTitle?: string;
  activePageContent?: string;
  onUpdatePage?: (id: string, updates: { content?: string; title?: string }) => void;
}

const AIPanel: React.FC<AIPanelProps> = ({ user, activePageId, activePageTitle, activePageContent, onUpdatePage }) => {
  return (
    <AIPanelContainer 
      user={user} 
      activePageId={activePageId}
      activePageTitle={activePageTitle}
      activePageContent={activePageContent}
      onUpdatePage={onUpdatePage}
    />
  );
};

export default AIPanel;
