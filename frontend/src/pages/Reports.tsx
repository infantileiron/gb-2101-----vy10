import type { Domain } from '../stores/domain';
import { domainStore } from '../stores/domain';
import { PageTitle } from '../components/common/PageTitle';
import { StatusBadge } from '../components/common/StatusBadge';
import { TrialSummary } from '../components/TrialSummary';
import { EmptyState } from '../components/common/EmptyState';
import { date } from '../utils/format';

export function Reports({ data, editable, act, busy }: { data: Domain; editable: boolean; act: (f: () => Promise<unknown>) => Promise<void>; busy: boolean }) {
  const approved = data.reviews.filter(r => r.status === 'approved' && !data.reports.some(p => p.review_id === r.id));
  return <>
    <PageTitle eyebrow="06 / ARCHIVE & HANDOFF" title="把口径和结论，一起交接。">复核通过才可生成报告。源数据更新后旧报告标记失效并停止下载沿用；新报告对应重算后的数据版本。</PageTitle>
    {editable && approved.map(r => (
      <section className="pending-archive" key={r.id}>
        <p>复核 {r.id} 已通过，可归档交接。</p>
        <button disabled={busy} onClick={() => act(() => domainStore.reports.create(r.run_id, r.id, '封膜B · 研发复核报告'))}>生成报告 →</button>
      </section>
    ))}
    {!data.reports.length && <EmptyState>先完成研发复核，再生成可追溯的报告。</EmptyState>}
    {data.reports.map(p => {
      const run = data.runs.find(r => r.id === p.run_id);
      const invalid = p.status === 'invalidated';
      return <section className="sheet" key={p.id}>
        <div className="section-title">
          <div>
            <p className="eyebrow">RESEARCH ARCHIVE / {date(p.created_at)}</p>
            <h2>{p.title}</h2>
          </div>
          {invalid ? <StatusBadge status="invalidated" /> : (
            <button className="secondary" onClick={() => act(() => domainStore.reports.download(p.id))}>下载 CSV ↗</button>
          )}
        </div>
        {invalid && <div className="invalid-banner">
          <b>报告已因源数据更新失效，停止沿用与下载。</b>
          {p.invalidated_reason}<br />
          失效时间：{new Date(p.invalidated_at).toLocaleString('zh-CN')} · 旧报告基于数据版本 v{run?.dataset_version}，请使用新版本重算并复核后生成的报告。
        </div>}
        {run && run.status === 'completed' && <TrialSummary run={run} />}
        <p className="annotation">报告 {p.id} · 关联复核 {p.review_id} · 数据版本 v{run?.dataset_version ?? '—'}。模拟数据用于流程演示。</p>
      </section>;
    })}
  </>;
}
