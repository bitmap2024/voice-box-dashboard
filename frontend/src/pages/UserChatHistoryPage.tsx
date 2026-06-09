import { useMemo, useState } from 'react';
import { ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Conversation, EndUser, PaginatedResponse } from '../types';

export function UserChatHistoryPage({ context, endUserId }: { context: AppContext; endUserId: string }) {
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const endUserUrl = context.factoryQuery
    ? `/api/end-users/${endUserId}?${context.factoryQuery}`
    : `/api/end-users/${endUserId}`;

  const endUser = useAsyncData(() => api<EndUser>(endUserUrl, { token: context.token }), [endUserUrl, context.token]);

  const query = useMemo(() => {
    const params = new URLSearchParams();
    params.set('page', String(page));
    params.set('page_size', String(pageSize));
    params.set('end_user_id', endUserId);
    if (context.factoryQuery) {
      const fq = new URLSearchParams(context.factoryQuery);
      fq.forEach((v, k) => params.set(k, v));
    }
    return `/api/conversations?${params.toString()}`;
  }, [page, endUserId, context.factoryQuery]);

  const conversations = useAsyncData(
    () => api<PaginatedResponse<Conversation>>(query, { token: context.token }),
    [query, context.token],
  );

  const totalPages = Math.max(1, Math.ceil((conversations.data?.total || 0) / pageSize));

  return (
    <>
      <PageHeader
        title={endUser.data?.nickname || '聊天记录'}
        description={
          endUser.data
            ? `用户 ID：${endUser.data.id} · 设备 SN：${endUser.data.device_sn || '-'}`
            : '加载用户信息...'
        }
        action={
          <button className="ghost-button" onClick={() => context.navigate({ page: 'user-ops' })}>
            <ArrowLeft size={16} />返回
          </button>
        }
      />

      <div className="panel elevated full-page-table">
        <div className="panel-title">对话记录（按时间倒序）</div>
        {conversations.loading ? (
          <div className="muted">加载对话记录...</div>
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>角色</th>
                  <th>轮数</th>
                  <th>总延迟</th>
                  <th>反馈</th>
                  <th>状态</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {(conversations.data?.items || []).map((item) => (
                  <tr key={item.id}>
                    <td>{item.started_at?.slice(0, 16).replace('T', ' ')}</td>
                    <td>{item.character_name}</td>
                    <td>{item.total_turns}</td>
                    <td>{item.total_latency_ms} ms</td>
                    <td>{item.feedback || '-'}</td>
                    <td><StatusBadge value={item.success ? 'resolved' : 'open'} /></td>
                    <td>
                      <button
                        className="link-button"
                        onClick={() => context.navigate({ page: 'conversation-detail', id: item.id })}
                      >
                        查看详情
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="toolbar" style={{ justifyContent: 'space-between', marginTop: '1rem' }}>
              <span className="muted">共 {conversations.data?.total || 0} 条，第 {page} / {totalPages} 页</span>
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
