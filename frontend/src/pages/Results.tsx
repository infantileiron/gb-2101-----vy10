import { useState } from 'react';
import type { Domain } from '../stores/domain';
import { domainStore } from '../stores/domain';
import { PageTitle } from '../components/common/PageTitle';
import { StatusBadge } from '../components/common/StatusBadge';
import { EmptyState } from '../components/common/EmptyState';
import { TrialSummary } from '../components/TrialSummary';
import { RunChart } from '../components/RunChart';
import { number } from '../utils/format';

export function Results({ data, editable, act, busy }: { data: Domain; editable: boolean; act: (f: () => Promise<unknown>) => Promise<void>; busy: boolean }) {
  const [id, setId] = useState(data.runs[0]?.id || '');
  const [comment, setComment] = useState('请复核站点效应一致性、排除口径与包装成本适用性。');
  const run = data.runs.find(r => r.id === id) || data.runs[0];
  if (!run) {
    return <>
      <PageTitle eyebrow="04 / COMPUTATION RECORD" title="看效应，也看它的边界。">每 5 秒更新。源数据补报生成新版本后，旧运行标记为已失效并保留依据，请基于新版本重算。</PageTitle>
      <EmptyState>在试验设计中提交计算，这里会展示后台任务与统计结果。</EmptyState>
    </>;
  }
  const invalid = run.status === 'invalidated';
  const exp = data.experiments.find(e => e.id === run.experiment_id);
  const ds = data.datasets.find(d => d.id === exp?.dataset_id);
  const reviewExists = data.reviews.some(r => r.run_id === run.id && r.status !== 'rejected');
  return <>
    <PageTitle eyebrow="04 / COMPUTATION RECORD" title="看效应，也看它的边界。">每 5 秒更新。源数据补报生成新版本后，旧运行标记为已失效并保留依据，请基于新版本重算。</PageTitle>
    <div className="run-tabs">
      {data.runs.map(r => {
        const name = data.experiments.find(e => e.id === r.experiment_id)?.name || r.id;
        return <button key={r.id} className={run.id === r.id ? 'selected' : ''} onClick={() => setId(r.id)}>{name} <StatusBadge status={r.status} /></button>;
      })}
    </div>

    {invalid && <section className="sheet">
      <StatusBadge status={run.status} />
      <div className="invalid-banner">
        <b>该分析依据的数据已更新，结果已失效，停止用于复核与报告。</b>
        {run.invalidated_reason}<br />
        失效时间：{new Date(run.invalidated_at).toLocaleString('zh-CN')} · 该运行基于数据版本 v{run.dataset_version}。下方保留旧版统计依据供追溯。
      </div>
      {run.result && <>
        <TrialSummary run={run} />
        <RunChart result={run.result} />
        <p className="annotation">以下为失效前的旧版结果，仅作留档，不代表当前数据结论。</p>
      </>}
      <p className="muted">请回到“试验设计”对同一方案重新提交计算，新运行将绑定当前数据版本。</p>
    </section>}

    {!invalid && run.status !== 'completed' && <section className="sheet">
      <StatusBadge status={run.status} />
      <p>{run.error || '后台正在处理观测，请稍候。'}</p>
    </section>}

    {!invalid && run.status === 'completed' && <>
      <TrialSummary run={run} />
      {ds && ds.current_version !== run.dataset_version && (
        <div className="invalid-banner"><b>数据版本提示</b>该运行基于 v{run.dataset_version}，数据集当前为 v{ds.current_version}。</div>
      )}
      <RunChart result={run.result} />
      <section className="sheet">
        <h2>站点与分组分布</h2>
        <table>
          <thead><tr><th>站点</th><th>A 批次</th><th>B 批次</th><th>权重</th><th>B − A</th></tr></thead>
          <tbody>{run.result.sites.map(s => (
            <tr key={s.station}><td>{s.station}</td><td>{s.A}</td><td>{s.B}</td><td>{number(s.weight * 100)}%</td><td>{number(s.effect)} pp</td></tr>
          ))}</tbody>
        </table>
        <p className="annotation">温度与失重率 Pearson r = {run.result.temperature_correlation === null ? '不可定义' : number(run.result.temperature_correlation, 3)}；相关性不表示因果。</p>
        <table>
          <thead><tr><th>组别</th><th>样本量</th><th>均值 / SD</th><th>Q25 / 中位 / Q75</th></tr></thead>
          <tbody>{run.result.groups.map(g => (
            <tr key={g.group}>
              <td>{g.group === 'A' ? 'A · 原包装' : 'B · 新封膜'}</td>
              <td>{g.n}</td><td>{number(g.mean)} / {number(g.sd)}</td>
              <td>{number(g.q25)} / {number(g.median)} / {number(g.q75)}</td>
            </tr>
          ))}</tbody>
        </table>
      </section>
      {editable && !reviewExists && <section className="sheet">
        <h2>提交研发复核</h2>
        <label>业务解释与待核事项
          <textarea value={comment} onChange={e => setComment(e.target.value)} minLength={5} />
        </label>
        <button disabled={busy} onClick={() => act(() => domainStore.reviews.create(run.id, comment))}>提交复核 →</button>
      </section>}
    </>}
  </>;
}
