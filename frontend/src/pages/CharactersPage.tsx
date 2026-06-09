import { useState } from 'react';
import { Plus } from 'lucide-react';
import { api, post } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Character } from '../types';

export function CharactersPage({ context }: { context: AppContext }) {
  const suffix = context.factoryQuery ? `?${context.factoryQuery}` : '';
  const { data, loading, setData } = useAsyncData(() => api<Character[]>(`/api/characters${suffix}`, { token: context.token }), [context.token, context.factoryQuery]);
  const [name, setName] = useState('');

  async function createCharacter() {
    if (!name.trim()) return;
    const row = await post<Character>('/api/characters', { name, scene_type: '故事陪伴', description: '新建 AI 角色' }, context.token);
    setData([...(data || []), row]);
    setName('');
  }

  return (
    <>
      <PageHeader title="角色 Prompt" description="配置 AI 语音角色、结构化 system prompt、版本发布与回滚。" />
      {context.user.role_code !== 'super_admin' && (
        <div className="toolbar">
          <input placeholder="新角色名称" value={name} onChange={(event) => setName(event.target.value)} />
          <button className="primary-button compact" onClick={createCharacter}><Plus size={16} />新增角色</button>
        </div>
      )}
      <div className="panel">
        {loading ? '加载角色...' : (
          <table>
            <thead>
              <tr><th>角色</th><th>场景</th><th>年龄段</th><th>语气</th><th>状态</th><th>绑定设备</th><th>今日对话</th><th>兜底率</th><th>平均延迟</th><th></th></tr>
            </thead>
            <tbody>
              {(data || []).map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>{item.scene_type}</td>
                  <td>{item.age_range}</td>
                  <td>{item.tone_style}</td>
                  <td><StatusBadge value={item.status} /></td>
                  <td>{item.bound_device_count}</td>
                  <td>{item.today_conversations}</td>
                  <td>{(item.fallback_rate * 100).toFixed(1)}%</td>
                  <td>{item.avg_latency_ms} ms</td>
                  <td><button className="link-button" onClick={() => context.navigate({ page: 'character-detail', id: item.id })}>配置</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
