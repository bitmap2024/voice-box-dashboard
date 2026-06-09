import { api, post } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Alert } from '../types';

export function AlertsPage({ context }: { context: AppContext }) {
  const suffix = context.factoryQuery ? `?${context.factoryQuery}` : '';
  const { data, loading, setData } = useAsyncData(() => api<Alert[]>(`/api/alerts${suffix}`, { token: context.token }), [context.token, context.factoryQuery]);

  async function resolve(id: string) {
    const row = await post<Alert>(`/api/alerts/${id}/resolve`, {}, context.token);
    setData((data || []).map((item) => (item.id === id ? row : item)));
  }

  return (
    <>
      <PageHeader title="告警日志" description="集中处理设备离线、弱网、对话失败、延迟超阈值和 Prompt 异常。" />
      <div className="panel">
        {loading ? '加载告警...' : (
          <table>
            <thead>
              <tr><th>等级</th><th>类型</th><th>设备</th><th>标题</th><th>内容</th><th>状态</th><th>时间</th><th></th></tr>
            </thead>
            <tbody>
              {(data || []).map((item) => (
                <tr key={item.id}>
                  <td><StatusBadge value={item.severity} /></td>
                  <td>{item.alert_type}</td>
                  <td>{item.device_sn}</td>
                  <td>{item.title}</td>
                  <td className="wide-cell">{item.content}</td>
                  <td><StatusBadge value={item.status} /></td>
                  <td>{item.created_at.slice(5, 16)}</td>
                  <td>{item.status === 'open' && <button className="link-button" onClick={() => resolve(item.id)}>处理</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
