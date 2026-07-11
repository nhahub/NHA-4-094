export interface ApiError {
  status: number;
  code?: string;
  message: string;
  details?: unknown;
}
