export interface Notification {
  id: string;
  type: 'CONTRIBUTION' | 'SUBSCRIPTION' | 'INVITE';
  title: string;
  body: string;
  time: string;
  read: boolean;
}
