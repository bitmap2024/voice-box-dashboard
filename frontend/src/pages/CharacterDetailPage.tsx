import { useState } from 'react';
import { ArrowLeft, Rocket } from 'lucide-react';
import { api, post } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Character, PromptVersion } from '../types';

type CharacterDetail = Character & { prompt_versions: PromptVersion[] };

export function CharacterDetailPage({ context, id }: { context: AppContext; id: string }) {
  const { data, loading, setData } = useAsyncData(() => api<CharacterDetail>('/api/characters/' + id, { token: context.token }), [context.token, id]);
  const [version, setVersion] = useState('v1.2');
  const [prompt, setPrompt] = useState('你是一个适合儿童的 AI 语音角色。回答要简短、安全、有引导性。');
  const [note, setNote] = useState('优化回复长度和主动引导');

  async function createVersion() {
    if (!data) return;
    const row = await post<PromptVersion>(`/api/characters/${id}/prompt-versions`, {
      version,
      system_prompt: prompt,
      change_note: note,
      structured_config: {
        role_identity: data.name,
        user_target: data.age_range,
        tone_style: data.tone_style,
        reply_length: '2 句话以内',
        active_guidance: true,
      },
    }, context.token);
    setData({ ...data, prompt_versions: [row, ...data.prompt_versions] });
  }

  async function publish(versionId: string) {
    await post<PromptVersion>(`/api/prompt-versions/${versionId}/publish`, {}, context.token);
    const fresh = await api<CharacterDetail>('/api/characters/' + id, { token: context.token });
    setData(fresh);
  }

  if (loading || !data) return <div className="panel">加载角色配置...</div>;

  return (
    <>
      <PageHeader
        title={data.name}
        description="结构化配置角色设定，并用版本管理保证线上 Prompt 可回滚。"
        action={<button className="ghost-button" onClick={() => context.navigate({ page: 'characters' })}><ArrowLeft size={16} />返回</button>}
      />
      <div className="grid two">
        <div className="panel">
          <div className="panel-title">角色基础信息</div>
          <div className="form-grid">
            <label>场景类型<input readOnly value={data.scene_type} /></label>
            <label>年龄段<input readOnly value={data.age_range} /></label>
            <label>语气风格<input readOnly value={data.tone_style} /></label>
            <label>状态<input readOnly value={data.status} /></label>
          </div>
          <p className="muted">{data.description}</p>
        </div>
        <div className="panel">
          <div className="panel-title">新建 Prompt 版本</div>
          <div className="form-grid">
            <label>版本号<input value={version} onChange={(event) => setVersion(event.target.value)} /></label>
            <label>修改说明<input value={note} onChange={(event) => setNote(event.target.value)} /></label>
          </div>
          <label>System Prompt<textarea rows={5} value={prompt} onChange={(event) => setPrompt(event.target.value)} /></label>
          <button className="primary-button compact" onClick={createVersion}><Rocket size={16} />保存草稿</button>
        </div>
      </div>
      <div className="panel">
        <div className="panel-title">版本历史</div>
        <table>
          <thead>
            <tr><th>版本</th><th>状态</th><th>说明</th><th>创建人</th><th>创建时间</th><th>Prompt</th><th></th></tr>
          </thead>
          <tbody>
            {data.prompt_versions.map((item) => (
              <tr key={item.id}>
                <td>{item.version}</td>
                <td><StatusBadge value={item.status} /></td>
                <td>{item.change_note}</td>
                <td>{item.created_by}</td>
                <td>{item.created_at.slice(0, 10)}</td>
                <td className="wide-cell">{item.system_prompt}</td>
                <td>{item.status !== 'published' && <button className="link-button" onClick={() => publish(item.id)}>发布</button>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
