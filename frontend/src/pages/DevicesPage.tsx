import { useState } from 'react';
import { Plus, Search } from 'lucide-react';
import { api, post } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Device } from '../types';

type DeviceResponse = { items: Device[]; total: number };

export function DevicesPage({ context }: { context: AppContext }) {
  const [keyword, setKeyword] = useState('');
  const [status, setStatus] = useState('');
  const [sn, setSn] = useState('');
  const factoryQuery = context.factoryQuery ? `&${context.factoryQuery}` : '';
  const url = `/api/devices?keyword=${encodeURIComponent(keyword)}&status=${status}${factoryQuery}`;
  const { data, loading, setData } = useAsyncData(() => api<DeviceResponse>(url, { token: context.token }), [context.token, keyword, status, context.factoryQuery]);

  async function bindDevice() {
    if (!sn.trim()) return;
    const row = await post<Device>('/api/devices/bind', { sn, mac_address: `A4:CF:12:${Date.now().toString().slice(-8)}`, model: 'VB-ESP32-S3' }, context.token);
    setData({ items: [row, ...(data?.items || [])], total: (data?.total || 0) + 1 });
    setSn('');
  }

  return (
    <>
      <PageHeader title="设备运维" description="管理 ESP32 盒子的 SN 绑定、在线状态、固件版本、网络质量和异常。" />
      <div className="toolbar">
        <div className="searchbox"><Search size={16} /><input placeholder="搜索 SN / MAC" value={keyword} onChange={(event) => setKeyword(event.target.value)} /></div>
        <select value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="">全部状态</option>
          <option value="online">在线</option>
          <option value="warning">异常</option>
          <option value="offline">离线</option>
        </select>
        {context.user.role_code !== 'super_admin' && (
          <>
            <input placeholder="绑定新 SN" value={sn} onChange={(event) => setSn(event.target.value)} />
            <button className="primary-button compact" onClick={bindDevice}><Plus size={16} />绑定</button>
          </>
        )}
      </div>
      <div className="panel">
        {loading ? '加载设备...' : (
          <table>
            <thead>
              <tr><th>SN</th><th>绑定用户</th><th>型号</th><th>状态</th><th>RSSI</th><th>RTT</th><th>固件</th><th>批次</th><th>今日对话</th><th>最近心跳</th><th></th></tr>
            </thead>
            <tbody>
              {(data?.items || []).map((device) => (
                <tr key={device.id}>
                  <td>{device.sn}</td>
                  <td>{device.bound_user?.nickname || '-'}</td>
                  <td>{device.model}</td>
                  <td><StatusBadge value={device.status} /></td>
                  <td>{device.wifi_rssi} dBm</td>
                  <td>{device.rtt_ms} ms</td>
                  <td>{device.firmware_version}</td>
                  <td>{device.batch_no}</td>
                  <td>{device.today_conversations}</td>
                  <td>{device.last_seen_at?.slice(5, 16) || '-'}</td>
                  <td><button className="link-button" onClick={() => context.navigate({ page: 'device-detail', id: device.id })}>详情</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
