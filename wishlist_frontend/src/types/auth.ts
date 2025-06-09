export interface UserType {
  id: number;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  avatar?: string;
  subscriptionType?: string;
  subscriptionEndDate?: string;
}

export interface AuthContextType {
  user: UserType | null;
  token: string | null;
  loading: boolean;
  login: (token: string, user: UserType) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (userData: Partial<UserType>) => Promise<void>;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
}
