import { useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Search, UserRound } from 'lucide-react';
import { api } from '../api';
import { PageHeader } from '../components/PageHeader';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { EndUser, PaginatedResponse } from '../types';

export function UserOpsPage({ context }: { context: AppContext }) {
  const showFactory = context.user.role_code === 'super_admin' && !context.selectedFactoryId;
  const [page, setPage] = useState(1);
  const [sn, setSn] = useState('');
  const [userId, setUserId] = useState('');
  const pageSize = 20;

  const query = useMemo(() => {
    const params = new URLSearchParams();
    params.set('page', String(page));
    params.set('page_size', String(pageSize));
    if (sn) params.set('sn', sn);
    if (userId) params.set('user_id', userId);
    if (context.factoryQuery) {
      const fq = new URLSearchParams(context.factoryQuery);
      fq.forEach((v, k) => params.set(k, v));
    }
    return `/api/end-users?${params.toString()}`;
  }, [page, sn, userId, context.factoryQuery]);

  const endUsers = useAsyncData(
    () => api<PaginatedResponse<EndUser>>(query, { token: context.token }),
    [query, context.token],
  );

  useEffect(() => {
    setPage(1);
  }, [sn, userId, context.factoryQuery]);

  const totalPages = Math.max(1, Math.ceil((endUsers.data?.total || 0) / pageSize));

  return (
    <>
      <PageHeader
        title="用户运营"
        description="查看设备绑定用户，支持按设备 SN 或用户 ID 检索，点击可查看完整聊天记录与链路分析。"
      />

      <div className="panel elevated full-page-table">
        <div className="panel-title"><UserRound size={18} />绑定用户概览</div>
        <div className="toolbar">
          <div className="searchbox">
            <Search size={16} />
            <input placeholder="设备 SN" value={sn} onChange={(e) => setSn(e.target.value)} />
          </div>
          <div className="searchbox">
            <Search size={16} />
            <input placeholder="用户 ID" value={userId} onChange={(e) => setUserId(e.target.value)} />
          </div>
        </div>

        {endUsers.loading ? (
          <div className="muted">加载用户...</div>
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>用户 ID</th>
                  {showFactory && <th>工厂</th>}
                  <th>昵称</th>
                  <th>设备 SN</th>
                  <th>年龄段</th>
                  <th>累计对话</th>
                  <th>最近活跃</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {(endUsers.data?.items || []).map((user) => (
                  <tr key={user.id}>
                    <td className="mono-cell">{user.id}</td>
                    {showFactory && <td>{user.factory_name}</td>}
                    <td>{user.nickname}</td>
                    <td>{user.device_sn || '-'}</td>
                    <td>{user.age_range || '-'}</td>
                    <td>{user.total_conversations}</td>
                    <td>{user.last_active_at?.slice(5, 16).replace('T', ' ') || '-'}</td>
                    <td>
                      <button
                        className="link-button"
                        onClick={() => context.navigate({ page: 'user-chat-history', endUserId: user.id })}
                      >
                        查看聊天记录
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="toolbar" style={{ justifyContent: 'space-between', marginTop: '1rem' }}>
              <span className="muted">共 {endUsers.data?.total || 0} 人，第 {page} / {totalPages} 页</span>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="ghost-button compact" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                  <ChevronLeft size={16} />上一页
                </button>
                <button className="ghost-button compact" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                  下一页<ChevronRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
