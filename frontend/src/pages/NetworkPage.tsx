import { RadioTower, Router, WifiOff } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Device } from '../types';

type NetworkData = {
  summary: { label: string; value: number; unit: string }[];
  weak_rank: Device[];
  rtt_rank: Device[];
  firmware_risk: { firmware: string; device_count: number; abnormal_rate: number }[];
  batch_risk: { batch_no: string; weak_rate: number; reconnect_rate: number }[];
};

export function NetworkPage({ context }: { context: AppContext }) {
  const suffix = context.factoryQuery ? `?${context.factoryQuery}` : '';
  const { data, loading } = useAsyncData(() => api<NetworkData>(`/api/network/summary${suffix}`, { token: context.token }), [context.token, context.factoryQuery]);

  return (
    <>
      <PageHeader title="网络时序" description="从批量设备维度回答：是云端问题、设备问题，还是用户 Wi-Fi 问题。" />
      {loading ? <div className="panel">加载网络监控...</div> : (
        <>
          <div className="quality-grid">
            {(data?.summary || []).map((item, index) => (
              <div className="quality-card" key={item.label}>
                <div className="quality-icon">{index === 1 ? <WifiOff size={18} /> : <RadioTower size={18} />}</div>
                <span>{item.label}</span>
                <strong>{item.value}<small>{item.unit}</small></strong>
                <em>{index === 0 ? '目标 > 90%' : '近 24 小时'}</em>
              </div>
            ))}
          </div>

          <div className="grid two">
            <div className="panel elevated">
              <div className="panel-title"><Router size={18} />固件版本异常率</div>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data?.firmware_risk || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="firmware" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="abnormal_rate" fill="#0f766e" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="panel elevated">
              <div className="panel-title">批次弱网风险</div>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data?.batch_risk || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="batch_no" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="weak_rate" fill="#f59e0b" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="reconnect_rate" fill="#2563eb" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid two">
            <div className="panel elevated">
              <div className="panel-title">弱网设备排行</div>
              <table className="data-table">
                <thead><tr><th>SN</th><th>状态</th><th>RSSI</th><th>固件</th><th>批次</th></tr></thead>
                <tbody>
                  {(data?.weak_rank || []).map((item) => (
                    <tr key={item.id}><td>{item.sn}</td><td><StatusBadge value={item.status} /></td><td>{item.wifi_rssi} dBm</td><td>{item.firmware_version}</td><td>{item.batch_no}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="panel elevated">
              <div className="panel-title">高 RTT 设备排行</div>
              <table className="data-table">
                <thead><tr><th>SN</th><th>RTT</th><th>RSSI</th><th>今日对话</th><th>最近心跳</th></tr></thead>
                <tbody>
                  {(data?.rtt_rank || []).map((item) => (
                    <tr key={item.id}><td>{item.sn}</td><td><strong>{item.rtt_ms} ms</strong></td><td>{item.wifi_rssi} dBm</td><td>{item.today_conversations}</td><td>{item.last_seen_at?.slice(5, 16)}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </>
  );
}
