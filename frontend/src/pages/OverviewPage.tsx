import { Activity, Lightbulb, RadioTower } from 'lucide-react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../api';
import { MetricCard } from '../components/MetricCard';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { Alert, Kpi } from '../types';
import type { AppContext } from '../App';

type Overview = {
  kpis: Kpi[];
  health: { online_rate: number; success_rate: number; weak_network_devices: number; open_alerts: number };
  alerts: Alert[];
  recommendations: { id: string; title: string; content: string; severity: string }[];
};

type Trends = {
  online: { label: string; value: number }[];
  conversations: { label: string; value: number }[];
  latency: { label: string; p50: number; p95: number }[];
};

export function OverviewPage({ context }: { context: AppContext }) {
  const suffix = context.factoryQuery ? `?${context.factoryQuery}` : '';
  const overview = useAsyncData(() => api<Overview>(`/api/dashboard/overview${suffix}`, { token: context.token }), [context.token, context.factoryQuery]);
  const trends = useAsyncData(() => api<Trends>(`/api/dashboard/trends${suffix}`, { token: context.token }), [context.token, context.factoryQuery]);

  if (overview.loading) return <div className="panel">加载总览数据...</div>;
  if (!overview.data) return <div className="panel">无法加载总览{overview.error ? `：${overview.error}` : ''}。</div>;

  return (
    <>
      <PageHeader title="今日体检报告" description="快速判断设备、对话链路、Prompt 运营和行业对标是否健康。" />
      <div className="metric-grid">
        {overview.data.kpis.map((item) => <MetricCard key={item.label} item={item} />)}
      </div>

      <div className="grid two">
        <div className="panel">
          <div className="panel-title"><RadioTower size={18} />在线设备趋势</div>
          {trends.loading ? (
            <div className="muted" style={{ padding: '2rem 0' }}>加载趋势数据...</div>
          ) : trends.data ? (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trends.data.online}>
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#0f766e" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="muted" style={{ padding: '2rem 0' }}>趋势数据暂不可用{trends.error ? `：${trends.error}` : ''}</div>
          )}
        </div>
        <div className="panel">
          <div className="panel-title"><Activity size={18} />首句延迟 P50 / P95</div>
          {trends.loading ? (
            <div className="muted" style={{ padding: '2rem 0' }}>加载趋势数据...</div>
          ) : trends.data ? (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trends.data.latency}>
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="p50" stroke="#2563eb" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="p95" stroke="#dc2626" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="muted" style={{ padding: '2rem 0' }}>趋势数据暂不可用{trends.error ? `：${trends.error}` : ''}</div>
          )}
        </div>
      </div>

      <div className="grid two">
        <div className="panel">
          <div className="panel-title">最近告警</div>
          <table>
            <tbody>
              {overview.data.alerts.map((alert) => (
                <tr key={alert.id}>
                  <td><StatusBadge value={alert.severity} /></td>
                  <td>{alert.title}</td>
                  <td className="muted">{alert.created_at?.slice(5, 16) ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="panel">
          <div className="panel-title"><Lightbulb size={18} />优化建议</div>
          <div className="stack">
            {overview.data.recommendations.map((item) => (
              <div className="suggestion" key={item.id}>
                <strong>{item.title}</strong>
                <p>{item.content}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
