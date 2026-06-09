import { api } from '../api';
import { PageHeader } from '../components/PageHeader';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { EndUser, PaginatedResponse } from '../types';

export function EndUsersPage({ context }: { context: AppContext }) {
  const suffix = context.factoryQuery ? `?${context.factoryQuery}` : '';
  const { data, loading } = useAsyncData(
    () => api<PaginatedResponse<EndUser>>(`/api/end-users${suffix}`, { token: context.token }),
    [context.token, context.factoryQuery],
  );

  return (
    <>
      <PageHeader
        title="终端用户"
        description={context.user.role_code === 'super_admin' ? '平台管理员可查看所有工厂设备绑定的终端用户及会话概况。' : '查看本工厂设备绑定的终端用户。'}
      />
      <div className="panel">
        {loading ? '加载中...' : (
          <table className="data-table">
            <thead>
              <tr>
                {context.user.role_code === 'super_admin' && !context.selectedFactoryId && <th>工厂</th>}
                <th>昵称</th>
                <th>绑定设备 SN</th>
                <th>年龄段</th>
                <th>地区</th>
                <th>累计对话</th>
                <th>最近活跃</th>
                <th>绑定时间</th>
              </tr>
            </thead>
            <tbody>
              {(data?.items || []).map((item) => (
                <tr key={item.id}>
                  {context.user.role_code === 'super_admin' && !context.selectedFactoryId && <td>{item.factory_name}</td>}
                  <td>{item.nickname}</td>
                  <td>{item.device_sn || '-'}</td>
                  <td>{item.age_range || '-'}</td>
                  <td>{item.region || '-'}</td>
                  <td>{item.total_conversations}</td>
                  <td>{item.last_active_at?.slice(5, 16) || '-'}</td>
                  <td>{item.bound_at?.slice(0, 10) || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
