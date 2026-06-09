import { Activity, AlertTriangle, BarChart3, Bell, Bot, Building2, Cpu, LayoutDashboard, LogOut, MessageSquareText, RadioTower, Users } from 'lucide-react';
import type { ReactNode } from 'react';
import type { Factory, User } from '../types';

export type PageKey = 'overview' | 'factories' | 'devices' | 'network' | 'characters' | 'user-ops' | 'latency' | 'users' | 'industry' | 'alerts';

type NavItem = {
  key: PageKey;
  label: string;
  icon: ReactNode;
  superOnly?: boolean;
};

const navItems: NavItem[] = [
  { key: 'overview', label: '总览', icon: <LayoutDashboard size={18} /> },
  { key: 'factories', label: '租户管理', icon: <Building2 size={18} />, superOnly: true },
  { key: 'devices', label: '设备运维', icon: <Cpu size={18} /> },
  { key: 'network', label: '网络时序', icon: <RadioTower size={18} /> },
  { key: 'characters', label: '角色 Prompt', icon: <Bot size={18} /> },
  { key: 'user-ops', label: '用户运营', icon: <MessageSquareText size={18} /> },
  { key: 'latency', label: '链路观测', icon: <Activity size={18} /> },
  { key: 'users', label: '后台用户', icon: <Users size={18} /> },
  { key: 'industry', label: '行业分析', icon: <BarChart3 size={18} /> },
  { key: 'alerts', label: '告警日志', icon: <AlertTriangle size={18} /> },
];

export function DashboardLayout({
  user,
  factories,
  selectedFactoryId,
  onFactoryChange,
  activePage,
  onNavigate,
  onLogout,
  children,
}: {
  user: User;
  factories: Factory[];
  selectedFactoryId: string;
  onFactoryChange: (factoryId: string) => void;
  activePage: PageKey;
  onNavigate: (page: PageKey) => void;
  onLogout: () => void;
  children: ReactNode;
}) {
  const visibleItems = navItems.filter((item) => !item.superOnly || user.role_code === 'super_admin');
  const selectedFactory = factories.find((factory) => factory.id === selectedFactoryId);
  const scopeName = user.role_code === 'super_admin'
    ? selectedFactory?.name || '全部工厂'
    : user.factory?.name || '当前工厂';

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">VB</div>
          <div>
            <strong>VoiceBox</strong>
            <span>AI 语音硬件 SaaS</span>
          </div>
        </div>
        <nav>
          {visibleItems.map((item) => (
            <button key={item.key} className={activePage === item.key ? 'nav-item active' : 'nav-item'} onClick={() => onNavigate(item.key)}>
              {item.icon}
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
        <div className="topbar-context">
            <div className="factory-name">{scopeName}</div>
            <div className="muted">{user.role.name} · {user.name} · 数据视角</div>
        </div>
        <div className="topbar-actions">
          {user.role_code === 'super_admin' && (
            <label className="factory-switcher">
              <span>查看工厂</span>
              <select value={selectedFactoryId} onChange={(event) => onFactoryChange(event.target.value)}>
                <option value="">全部工厂</option>
                {factories.map((factory) => <option key={factory.id} value={factory.id}>{factory.name}</option>)}
              </select>
            </label>
          )}
          <div className="time-filter"><span>今日</span><strong>实时监控</strong></div>
          <button className="icon-button" title="告警">
            <Bell size={18} />
            </button>
            <button className="ghost-button" onClick={onLogout}>
              <LogOut size={16} />
              退出
            </button>
          </div>
        </header>
        <section className="content">{children}</section>
      </main>
    </div>
  );
}
