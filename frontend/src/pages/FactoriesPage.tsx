import { useState } from 'react';
import { Plus } from 'lucide-react';
import { api, post } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Factory } from '../types';

export function FactoriesPage({ context }: { context: AppContext }) {
  const { data, loading, setData } = useAsyncData(() => api<Factory[]>('/api/factories', { token: context.token }), [context.token]);
  const [name, setName] = useState('');

  async function createFactory() {
    if (!name.trim()) return;
    const row = await post<Factory>('/api/factories', { name, industry: 'AI 玩具', plan_type: 'Professional' }, context.token);
    setData([...(data || []), row]);
    setName('');
  }

  return (
    <>
      <PageHeader title="租户管理" description="平台方管理工厂租户、行业、套餐和服务状态。" />
      {context.user.role_code === 'super_admin' && (
        <div className="toolbar">
          <input placeholder="新工厂名称" value={name} onChange={(event) => setName(event.target.value)} />
          <button className="primary-button compact" onClick={createFactory}><Plus size={16} />新增工厂</button>
        </div>
      )}
      <div className="panel">
        {loading ? '加载中...' : (
          <table>
            <thead>
              <tr><th>工厂</th><th>行业</th><th>套餐</th><th>设备额度</th><th>状态</th><th>创建时间</th></tr>
            </thead>
            <tbody>
              {(data || []).map((factory) => (
                <tr key={factory.id}>
                  <td>{factory.name}</td>
                  <td>{factory.industry}</td>
                  <td>{factory.plan_type}</td>
                  <td>{factory.device_quota}</td>
                  <td><StatusBadge value={factory.status} /></td>
                  <td>{factory.created_at.slice(0, 10)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
