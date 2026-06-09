import { useEffect, useMemo, useState } from 'react';
import { api } from './api';
import { DashboardLayout, PageKey } from './layouts/DashboardLayout';
import { LoginPage } from './pages/LoginPage';
import { OverviewPage } from './pages/OverviewPage';
import { FactoriesPage } from './pages/FactoriesPage';
import { DevicesPage } from './pages/DevicesPage';
import { DeviceDetailPage } from './pages/DeviceDetailPage';
import { CharactersPage } from './pages/CharactersPage';
import { CharacterDetailPage } from './pages/CharacterDetailPage';
import { UserOpsPage } from './pages/UserOpsPage';
import { UserChatHistoryPage } from './pages/UserChatHistoryPage';
import { ConversationDetailPage } from './pages/ConversationDetailPage';
import { LatencyPage } from './pages/LatencyPage';
import { NetworkPage } from './pages/NetworkPage';
import { UsersPage } from './pages/UsersPage';
import { IndustryPage } from './pages/IndustryPage';
import { AlertsPage } from './pages/AlertsPage';
import type { User } from './types';
import type { Factory } from './types';

export type AppView =
  | { page: PageKey }
  | { page: 'device-detail'; id: string }
  | { page: 'character-detail'; id: string }
  | { page: 'user-chat-history'; endUserId: string }
  | { page: 'conversation-detail'; id: string };

export type AppContext = {
  token: string;
  user: User;
  selectedFactoryId: string;
  factoryQuery: string;
  navigate: (view: AppView) => void;
  refreshMe: () => Promise<void>;
};

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('voicebox_token') || '');
  const [user, setUser] = useState<User | null>(null);
  const [factories, setFactories] = useState<Factory[]>([]);
  const [selectedFactoryId, setSelectedFactoryId] = useState('');
  const [view, setView] = useState<AppView>({ page: 'overview' });
  const [booting, setBooting] = useState(Boolean(token));

  async function refreshMe() {
    const me = await api<User>('/api/auth/me', { token });
    setUser(me);
  }

  useEffect(() => {
    if (!token) return;
    api<User>('/api/auth/me', { token })
      .then((me) => {
        setUser(me);
        if (me.factory_id) setSelectedFactoryId(me.factory_id);
        return api<Factory[]>('/api/factories', { token });
      })
      .then(setFactories)
      .catch(() => {
        localStorage.removeItem('voicebox_token');
        setToken('');
      })
      .finally(() => setBooting(false));
  }, [token]);

  const context = useMemo<AppContext | null>(() => {
    if (!token || !user) return null;
    const scopedFactoryId = user.role_code === 'super_admin' ? selectedFactoryId : user.factory_id || '';
    return {
      token,
      user,
      selectedFactoryId: scopedFactoryId,
      factoryQuery: scopedFactoryId ? `factory_id=${encodeURIComponent(scopedFactoryId)}` : '',
      navigate: setView,
      refreshMe,
    };
  }, [token, user, selectedFactoryId]);

  if (booting) return <div className="center-screen">加载控制台...</div>;

  if (!context) {
    return (
      <LoginPage
        onLogin={(nextToken, nextUser) => {
          localStorage.setItem('voicebox_token', nextToken);
          setToken(nextToken);
          setUser(nextUser);
          setSelectedFactoryId(nextUser.factory_id || '');
          api<Factory[]>('/api/factories', { token: nextToken }).then(setFactories).catch(() => setFactories([]));
        }}
      />
    );
  }

  const activePage =
    view.page === 'device-detail' ? 'devices'
    : view.page === 'character-detail' ? 'characters'
    : view.page === 'user-chat-history' || view.page === 'conversation-detail' ? 'user-ops'
    : view.page;

  return (
    <DashboardLayout
      user={context.user}
      factories={factories}
      selectedFactoryId={selectedFactoryId}
      onFactoryChange={setSelectedFactoryId}
      activePage={activePage}
      onNavigate={(page) => setView({ page })}
      onLogout={() => {
        localStorage.removeItem('voicebox_token');
        setToken('');
        setUser(null);
      }}
    >
      {renderPage(view, context)}
    </DashboardLayout>
  );
}

function renderPage(view: AppView, context: AppContext) {
  switch (view.page) {
    case 'overview':
      return <OverviewPage context={context} />;
    case 'factories':
      return <FactoriesPage context={context} />;
    case 'devices':
      return <DevicesPage context={context} />;
    case 'device-detail':
      return <DeviceDetailPage context={context} id={view.id} />;
    case 'characters':
      return <CharactersPage context={context} />;
    case 'network':
      return <NetworkPage context={context} />;
    case 'character-detail':
      return <CharacterDetailPage context={context} id={view.id} />;
    case 'user-ops':
      return <UserOpsPage context={context} />;
    case 'user-chat-history':
      return <UserChatHistoryPage context={context} endUserId={view.endUserId} />;
    case 'conversation-detail':
      return <ConversationDetailPage context={context} id={view.id} />;
    case 'users':
      return <UsersPage context={context} />;
    case 'latency':
      return <LatencyPage context={context} />;
    case 'industry':
      return <IndustryPage context={context} />;
    case 'alerts':
      return <AlertsPage context={context} />;
    default:
      return <OverviewPage context={context} />;
  }
}
