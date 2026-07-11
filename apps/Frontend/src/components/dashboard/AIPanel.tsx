import React from 'react';
import { AIPanelContainer } from './ai/AIPanelContainer';
import { User } from '@supabase/supabase-js';

interface AIPanelProps {
  user: User;
  activePageId?: string;
  activePageContent?: string;
  onUpdatePage?: (id: string, updates: { content: string }) => void;
}

const AIPanel: React.FC<AIPanelProps> = ({ user, activePageId, activePageContent, onUpdatePage }) => {
  return (
    <AIPanelContainer 
      user={user} 
      activePageId={activePageId}
      activePageContent={activePageContent}
      onUpdatePage={onUpdatePage}
    />
  );
};

export default AIPanel;
