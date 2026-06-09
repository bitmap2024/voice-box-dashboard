import { ArrowLeft } from 'lucide-react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Alert, Conversation, Device } from '../types';

type Telemetry = { timestamp: string; online: boolean; wifi_rssi: number; rtt_ms: number; reconnect_count: number };

export function DeviceDetailPage({ context, id }: { context: AppContext; id: string }) {
  const device = useAsyncData(() => api<Device & { character?: { name: string } }>('/api/devices/' + id, { token: context.token }), [context.token, id]);
  const telemetry = useAsyncData(() => api<Telemetry[]>('/api/devices/' + id + '/telemetry', { token: context.token }), [context.token, id]);
  const conversations = useAsyncData(() => api<Conversation[]>('/api/devices/' + id + '/conversations', { token: context.token }), [context.token, id]);
  const alerts = useAsyncData(() => api<Alert[]>('/api/devices/' + id + '/alerts', { token: context.token }), [context.token, id]);

  if (device.loading || !device.data) return <div className="panel">加载设备详情...</div>;

  return (
    <>
      <PageHeader
        title={device.data.sn}
        description="单设备基础信息、网络状态时序、最近对话和异常日志。"
        action={<button className="ghost-button" onClick={() => context.navigate({ page: 'devices' })}><ArrowLeft size={16} />返回</button>}
      />
      <div className="grid four">
        <div className="info-tile"><span>绑定用户</span><strong>{device.data.bound_user?.nickname || '未绑定'}</strong></div>
        <div className="info-tile"><span>状态</span><StatusBadge value={device.data.status} /></div>
        <div className="info-tile"><span>固件</span><strong>{device.data.firmware_version}</strong></div>
        <div className="info-tile"><span>当前角色</span><strong>{device.data.character?.name || '-'}</strong></div>
        <div className="info-tile"><span>网络</span><strong>{device.data.wifi_rssi} dBm / {device.data.rtt_ms} ms</strong></div>
        {device.data.bound_user && (
          <>
            <div className="info-tile"><span>用户地区</span><strong>{device.data.bound_user.region || '-'}</strong></div>
            <div className="info-tile"><span>累计对话</span><strong>{device.data.bound_user.total_conversations} 次</strong></div>
          </>
        )}
      </div>
      <div className="grid two">
        <div className="panel">
          <div className="panel-title">Wi-Fi RSSI</div>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={telemetry.data || []}>
              <XAxis dataKey="timestamp" tickFormatter={(v) => String(v).slice(11, 16)} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="wifi_rssi" stroke="#0f766e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="panel">
          <div className="panel-title">WebSocket RTT</div>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={telemetry.data || []}>
              <XAxis dataKey="timestamp" tickFormatter={(v) => String(v).slice(11, 16)} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="rtt_ms" stroke="#2563eb" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="grid two">
        <div className="panel">
          <div className="panel-title">最近对话</div>
          <table>
            <tbody>
              {(conversations.data || []).map((item) => (
                <tr key={item.id}><td>{item.started_at.slice(5, 16)}</td><td>{item.total_turns} 轮</td><td>{item.total_latency_ms} ms</td><td>{item.success ? '成功' : '失败'}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="panel">
          <div className="panel-title">异常日志</div>
          <table>
            <tbody>
              {(alerts.data || []).map((item) => (
                <tr key={item.id}><td><StatusBadge value={item.severity} /></td><td>{item.title}</td><td>{item.status}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
