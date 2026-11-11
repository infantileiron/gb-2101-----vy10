import { useState } from 'react';
import type { Domain } from '../stores/domain';
import type { Dataset, DatasetVersion, Supplement, SupplementEntry } from '../types/entities';
import { domainStore } from '../stores/domain';
import { PageTitle } from '../components/common/PageTitle';
import { EmptyState } from '../components/common/EmptyState';
import { StatusBadge } from '../components/common/StatusBadge';
import { supplementOutcome } from '../constants/enums';
import { date } from '../utils/format';

const outcomeClass: Record<SupplementEntry['outcome'], string> = {
  applied: 'outcome-applied',
  duplicate: 'outcome-duplicate',
  stale: 'outcome-stale',
  quarantined: 'outcome-quarantined',
};

export function Datasets({ data, editable, act, busy }: { data: Domain; editable: boolean; act: (f: () => Promise<unknown>) => Promise<void>; busy: boolean }) {
  const [selected, setSelected] = useState<Dataset | null>(null);
  const [name, setName] = useState('新增包装试验批次');
  const [text, setText] = useState('');
  const [supText, setSupText] = useState('');
  const [revision, setRevision] = useState(1);
  const [supplements, setSupplements] = useState<Supplement[]>([]);
  const [openSup, setOpenSup] = useState<string | null>(null);
  const [versionView, setVersionView] = useState<DatasetVersion | null>(null);

  async function openDataset(id: string) {
    const detail = await domainStore.datasets.detail(id);
    setSelected(detail);
    setVersionView(null);
    setSupplements(await domainStore.datasets.supplements(id));
  }

  async function submitSupplement() {
    if (!selected) return;
    const sup = await domainStore.datasets.submitSupplement(selected.id, { source: 'resubmission.csv', revision, csv_text: supText });
    setSupText('');
    const detail = await domainStore.datasets.detail(selected.id);
    setSelected(detail);
    setSupplements(await domainStore.datasets.supplements(detail.id));
    setOpenSup(sup.id);
  }

  async function viewVersion(version: number) {
    if (!selected) return;
    setVersionView(await domainStore.datasets.version(selected.id, version));
  }

  return <>
    <PageTitle eyebrow="02 / OBSERVATION REGISTER" title="每一批观测，都有出处。">
      批次编号唯一，失重率单位为百分比；站点补报按修订号进入同一数据集，重复不新增、旧修订不覆盖、同号异值逐条隔离。
    </PageTitle>

    <section className="sheet">
      <div className="section-title"><h2>数据批次</h2><span>{data.datasets.length} 个数据集</span></div>
      <table>
        <thead><tr><th>数据集 / 来源文件</th><th>当前版本</th><th>最新修订号</th><th>站点</th><th>观测数</th><th></th></tr></thead>
        <tbody>{data.datasets.map(d => <tr key={d.id}>
          <td><b>{d.name}</b><small>{d.source}</small></td>
          <td><span className="version-tag">v{d.current_version} · {d.version_count} 个版本</span></td>
          <td>r{d.latest_revision}</td>
          <td>{d.stations.join(' / ')}</td>
          <td>{d.row_count}</td>
          <td><button className="text-button" onClick={() => act(() => openDataset(d.id))}>检查观测与补报 →</button></td>
        </tr>)}</tbody>
      </table>
    </section>

    {selected && <section className="sheet">
      <div className="section-title">
        <h2>{selected.name} · {versionView ? `版本 v${versionView.version} 依据` : `当前版本 v${selected.current_version}`}</h2>
        <span>共 {(versionView?.rows ?? selected.rows)?.length} 条，未截断存储</span>
      </div>
      {versionView && <p className="quarantine-note">
        正在查看历史版本 v{versionView.version}（{date(versionView.created_at)}）的旧版依据，仅用于追溯，不参与新的复核与报告。
        <button className="text-button" onClick={() => setVersionView(null)} style={{ marginLeft: 12 }}>返回当前版本 →</button>
      </p>}
      <table>
        <thead><tr><th>批次</th><th>站点</th><th>组别</th><th>失重率 %</th><th>温度 ℃</th><th>修订号</th></tr></thead>
        <tbody>{(versionView?.rows ?? selected.rows)?.slice(0, 20).map(r => <tr key={r.batch_id}>
          <td>{r.batch_id}</td><td>{r.station}</td><td>{r.group}</td><td>{r.loss}</td><td>{r.temperature}</td><td>r{r.revision ?? 0}</td>
        </tr>)}</tbody>
      </table>
    </section>}

    {selected && <section className="sheet">
      <div className="section-title"><h2>数据版本时间线</h2><span>新版本只在补报实际应用后产生</span></div>
      <div className="version-timeline">
        {selected.versions?.map(v => <div className="v-row" key={v.version}>
          <span className={'v-dot' + (v.version === selected.current_version ? ' current' : '')}>v{v.version}</span>
          <div className="v-body">
            <b>{v.note}</b>
            <small>{date(v.created_at)} · {v.source} · {v.row_count} 条 · SHA256 {v.checksum.slice(0, 16)}…</small>
          </div>
          <button className="text-button" onClick={() => act(() => viewVersion(v.version))}>查看该版依据 →</button>
        </div>)}
      </div>
    </section>}

    {selected && <section className="sheet">
      <div className="section-title"><h2>补报处理明细</h2><span>{supplements.length} 次补报</span></div>
      {!supplements.length && <p className="muted">暂无补报记录。</p>}
      {supplements.map(s => <div key={s.id} style={{ borderBottom: '1px solid var(--line)', padding: '14px 0' }}>
        <div className="section-title" style={{ marginBottom: 6 }}>
          <h2 style={{ fontSize: 15 }}>补报 {s.id} · 修订号 r{s.revision}</h2>
          <StatusBadge status={s.status} />
        </div>
        <div className="supplement-meta">
          <span>来源 <b>{s.source}</b></span>
          <span>应用 <b>{s.applied_count}</b></span>
          <span>重复 <b>{s.duplicate_count}</b></span>
          <span>晚到旧修订 <b>{s.stale_count}</b></span>
          <span>隔离 <b>{s.quarantined_count}</b></span>
          <span>生成版本 <b>{s.new_version ? 'v' + s.new_version : '无'}</b></span>
          <span>{date(s.created_at)}</span>
        </div>
        {s.status === 'quarantined' && <p className="quarantine-note">
          存在同号异值条目，已逐条隔离且未覆盖任何现存观测，也未生成新版本；请核对来源后用更高修订号重新补报。
        </p>}
        <button className="text-button" onClick={() => setOpenSup(openSup === s.id ? null : s.id)}>
          {openSup === s.id ? '收起逐条明细' : '查看逐条处理原因 →'}
        </button>
        {openSup === s.id && <table style={{ marginTop: 12 }}>
          <thead><tr><th>批次</th><th>修订号</th><th>补报值 (loss/temp)</th><th>处理结果</th><th>原因说明</th></tr></thead>
          <tbody>{s.detail.map((e, i) => <tr key={e.batch_id + i}>
            <td>{e.batch_id}</td>
            <td>r{e.revision}</td>
            <td>{e.loss} / {e.temperature}</td>
            <td className={outcomeClass[e.outcome]}>{supplementOutcome[e.outcome]}</td>
            <td className="muted">{e.reason}</td>
          </tr>)}</tbody>
        </table>}
      </div>)}
    </section>}

    {editable && selected && <section className="sheet">
      <h2>向该数据集补报称重数据</h2>
      <p className="muted">
        表头与导入一致：batch_id,station,group,loss,temperature。补报必须带修订号：同号同值视为重复不新增；
        修订号低于现存记录视为晚到旧修订不覆盖；同号异值逐条隔离。仅当有条目实际应用时才生成新版本并使旧分析失效。
      </p>
      <form onSubmit={e => { e.preventDefault(); act(submitSupplement); }}>
        <label>本次补报修订号
          <input type="number" min={1} value={revision} onChange={e => setRevision(+e.target.value)} required />
        </label>
        <label>补报 CSV 文件
          <input type="file" accept=".csv,text/csv" onChange={async e => { const f = e.target.files?.[0]; if (f) setSupText(await f.text()); }} />
        </label>
        <label>补报 CSV 内容
          <textarea rows={5} value={supText} onChange={e => setSupText(e.target.value)} placeholder="batch_id,station,group,loss,temperature" required />
        </label>
        <button disabled={busy}>校验并处理补报</button>
      </form>
    </section>}

    {editable && <section className="sheet">
      <h2>导入新一批观测</h2>
      <p className="muted">表头：batch_id,station,group,loss,temperature · A为对照，B为新封膜，最多5000行。需要修订既有批次请使用上方补报，而非另建数据集。</p>
      <form onSubmit={e => { e.preventDefault(); act(async () => { await domainStore.datasets.create({ name, source: 'uploaded.csv', csv_text: text }); setText(''); }); }}>
        <label>数据集名称<input value={name} onChange={e => setName(e.target.value)} required /></label>
        <label>CSV 文件<input type="file" accept=".csv,text/csv" onChange={async e => { const f = e.target.files?.[0]; if (f) setText(await f.text()); }} /></label>
        <label>CSV 内容<textarea rows={5} value={text} onChange={e => setText(e.target.value)} placeholder="batch_id,station,group,loss,temperature" required /></label>
        <button disabled={busy}>校验并保存</button>
      </form>
    </section>}

    {!data.datasets.length && <EmptyState>上传逐批观测 CSV 后再创建试验。</EmptyState>}
  </>;
}
