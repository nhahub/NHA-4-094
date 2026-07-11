export interface SessionResponse {
  id: string;
  user_id: string;
  document_id?: string | null;
  created_at: string;
  updated_at: string;
  title?: string;
}

export interface MessageItem {
  id: string;
  session_id: string;
  user_id: string;
  role: "user" | "assistant";
  content: string;
  topic?: string | null;
  created_at: string;
}

export interface SessionMessagesResponse {
  session_id: string;
  messages: MessageItem[];
}
