export interface AuthUser {
  id: string;
  username: string;
  display_name: string;
}

export interface StoredDemoSession {
  user: AuthUser;
  startedAt: number;
}
