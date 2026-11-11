# 青禾鲜品 · 保鲜包装随机试验

以冷链站点为分层单位，从逐批观测计算包装效应、随机置换 p 值与 Bootstrap 区间，再经研发复核交接采购。中型全栈工程，五服务独立部署。

## 真实业务场景

模拟客户是青禾鲜品成都研发组，12 人，3 个冷链站。上游每日将鲜切叶菜称重结果导出为 `packaging_trial_202611.csv`。过去用 Excel 直接比较两个包装的均值：站点环境差异与包装组混杂、反复查看显著性、排除异常批次没有留痕。此工程替代“试验方案—统计计算—研发复核”这一段，下游由采购结合材料成本与运输损耗决定是否继续验证，不处理采购交易。

初始数据全部为固定随机种子生成的模拟数据，不能据此推断实际包装产品效果。

## 功能与实体

六个业务页面：实验总览、数据批次、试验设计、计算结果、研发复核、成果归档。登录独立。五个核心实体均贯穿数据库、Python model/schema、service/controller/route、前端 API/store、页面：

| 实体 | 表 | 业务动作 | 前端页面 |
|---|---|---|---|
| Dataset | datasets / supplements | CSV 校验、持久化、逐批检查、带修订号补报与版本留痕 | 数据批次 |
| Experiment | experiments | 固定数据集、排除阈值、随机种子与重采样数 | 试验设计 |
| AnalysisRun | runs | Redis 排队、后台计算、状态与失败原因、数据版本与失效标记 | 计算结果、总览 |
| Review | reviews | 分析员提交、负责人通过或退回、随源数据更新自动失效 | 研发复核 |
| Report | reports | 验证复核关系、生成共享卷 CSV、授权下载、失效后停止沿用 | 成果归档 |

共享业务组件 `TrialSummary` 用于总览、计算结果、复核、归档；`RunChart` 用于总览与结果。公共组件 `PageTitle`、`StatusBadge`、`EmptyState`；hooks `useSession`、`useResource`。图表数据由后端计算返回，不在前端构造统计结果。

## 角色与演示账号

| 角色 | 邮箱 | 页面与权限 | 典型动作 |
|---|---|---|---|
| admin | admin@qinghe.demo | 全部分析操作、最终复核 | 审批或退回复核 |
| analyst | analyst@qinghe.demo | 查看、导入、建方案、运行、提交复核、生成报告 | 运行站点分层分析 |
| viewer | viewer@qinghe.demo | 只读所有业务页，下载通过复核的报告 | 查看证据，下载报告 |

三个账号统一密码 **Qinghe2026!**。JWT 采用 HS256、有效期 8 小时，密码采用带独立 salt 的 PBKDF2-SHA256。角色鉴权在 API 执行，非只隐藏按钮。变更请求记录 actor、路径、时间与状态到审计表。全局错误处理中间件给出可恢复反馈；待执行/执行中任务最多 10 个。

## 快速启动

要求 Docker Engine 与 Compose v2 可访问，镜像/包源网络可用。项目路径可以含中文，Compose 使用明确短名。

```bash
cp .env.example .env
docker compose config --quiet
docker compose up -d --build
docker compose ps
docker compose exec -T backend python -m scripts.seed_demo
```

访问前端 <http://localhost:18200>；后端 OpenAPI <http://localhost:19200/docs>；数据库宿主端口 17700。浏览器通过 Nginx `/api/` 转发，后端路由本身不带 `/api`。Redis 和 worker 不映射宿主端口。

Compose 恰好五服务：frontend、backend、worker、db、redis，均有真实 healthcheck。backend/worker 等待数据库与 Redis healthy，frontend 等待 backend healthy。数据库卷 `db-data`、Redis AOF 卷 `redis-data`、共享产物卷 `shared-artifacts`。worker 每三秒更新心跳文件；分析输出 JSON、报告 CSV 写入共享产物卷。

清理：

```bash
docker compose down -v --remove-orphans
```

此命令会删除本项目演示数据卷。

## 一天的工作剧本

1. 09:00，陈昱用 analyst 账号登录，检查 `packaging_trial_202611.csv`，共 480 批、三个站点、A/B 各 240 批。
2. 09:05，在数据批次打开逐批观测，核对 `QH-202611-0001` 等批次编号、温度、失重率。
3. 09:10，在试验设计创建“封膜B · 新一轮站点复核”，选择上述数据，排除失重率 >15% 的批次。
4. 09:12，置换/Bootstrap 各 999 次，seed=202611，保存并提交计算。后台 worker 从 Redis 取任务。
5. 09:15，在计算结果核对 B−A 效应、95% 区间、双侧 p 值、站点权重和 Pearson 相关性；明确单位为失重率百分点 pp。
6. 09:20，填写业务解释与待核事项，提交研发复核。
7. 09:30，何婧用 admin 账号核对口径和成本假设，通过或退回复核。
8. 09:35，分析员在成果归档生成报告，许珂用 viewer 下载 CSV，报告包括 seed 与输入 SHA256。

初始还提供一个 1999 次重采样的独立复核方案及待审记录，便于演示管理员动作。

## 两个算法与口径

输入每行为 `batch_id,station,group,loss,temperature`。A 为原包装，B 为新封膜。`loss` 是 0–100 的失重百分率，温度为 −30–60℃。批次编号必须非空且唯一；只接收有限数值。最多 5000 行，每站每组排除后至少 5 批。

1. **站点分层双侧置换检验**：先按排除阈值筛选，站点权重 `w_s=n_s/N`。观测量 `Δ=Σ_s w_s(mean(B_s)−mean(A_s))`。每次只在本站混合观测内打乱组标签，保持本站 A/B 数量，重算 Δ。`p=(1+Σ(|Δ_perm|≥|Δ_obs|))/(iterations+1)`。正负号均可；负值表示 B 失重较少。前端直方图来自实际置换零分布。
2. **站点×组别 Bootstrap 百分位区间**：每站每组按原始样本数有放回抽样，权重固定，计算加权差，取 2.5%、97.5% 线性分位数。与置换共用 iterations、seed。区间假定站点组内批次独立，未处理运输批次间相关或重复测量。固定 seed 与相同输入顺序可精确复现；输入 checksum 记录原始 JSON 行序。

附带各组均值、样本标准差、四分位数，及温度和失重率的 Pearson r；零方差时 r 返回 null。不会把相关性说成因果。空组、样本不足、阈值无效会产生明确失败记录，禁止生成其复核和报告。

## 称重补报、修订号与数据版本

站点会补报称重数据。更正不再另建数据集，而是向原数据集提交带**修订号（revision）**的补报文件（`POST /datasets/{id}/supplements`，表头与导入一致）。系统按 `batch_id` 逐条比对现存记录，处理结果写入 `supplements` 表并可在数据批次页逐条查看原因：

| 情形 | 判定 | 处理 |
|---|---|---|
| 同修订号且观测值完全相同 | `duplicate` 重复投递 | 不新增观测、不生成新版本 |
| 补报修订号低于现存修订号 | `stale` 晚到旧修订 | 保留新值，绝不覆盖 |
| 同修订号但观测值不同 | `quarantined` 同号异值 | 逐条隔离、写明现存值与补报值，不覆盖、不生成新版本 |
| 新批次，或更高修订号且通过校验 | `applied` | 写入并生成新数据版本 |

数据集维护完整 `versions` 快照（版本号、来源、时间、行数、SHA256、全部行），新版本只在有条目实际应用时产生；同一份补报重复提交保持幂等。观测行带 `revision` 字段，初始导入为 r0。

**失效传导**：新版本生成后，所有基于旧版本完成的 AnalysisRun 标记为 `invalidated`（保留旧结果与共享卷 JSON 作为依据），其复核同步 `invalidated`、报告同步失效——复核审批与报告下载随即被后端拒绝，旧结果在重算期间仍可在页面查看。对同一方案重新提交计算得到的新运行绑定 `dataset_version`（当前版本），复核与报告基于新结果重建。运行在计算途中若数据集被更新，完成时会回读状态，不会把自身从失效改回完成。运行结果与报告 CSV 均记录对应数据版本。

## Seed 与本地开发

`SEED_DEMO=true` 时启动后执行 seed；失败记录日志，API 启动不因 seed 失败而阻塞。`python -m scripts.seed_demo` 可重复执行，所有演示记录按稳定自然键 insert-on-conflict-do-nothing，不增加副本、不覆盖用户改名或审批。首次生成 480 条观测、2 个试验、2 个完成运行、1 通过/1 待审复核、1 报告和3账号。

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
DATABASE_URL=sqlite:////tmp/fresh-trial-local.sqlite TASK_MODE=inline .venv/bin/uvicorn src.main:app --port 19200
```

SQLite/inline 为显式本地开发适配器，方便算法和 API 验证；容器固定 PostgreSQL/Redis，不得把本地适配器结果当作容器验收。开发前端：`cd frontend && npm install && npm run dev -- --port 18200`，Vite 会把 `/api` 代理到 19200。

导出演示输入：在 backend 下执行 `python -m scripts.export_demo > /tmp/packaging_trial_202611.csv`。

## 技术与结构

| 层 | 技术 |
|---|---|
| frontend | React 18.3.1、TypeScript 5.7、Vite 6、Nginx 1.27 |
| backend | Python 3.11、FastAPI 0.115、Pydantic 2.9 |
| worker | Python 独立进程、Redis 队列、实际统计重采样 |
| persistence | PostgreSQL 16、psycopg 3；本地 SQLite 仅开发适配 |
| cache / broker | Redis 7 AOF |

`frontend/src/` 按 api、stores、types、components/common、hooks、pages、router、utils、constants 分层；`backend/src/` 按 routes、controllers、services、models、schemas、middlewares、utils、constants、config 分层；`backend/migrations/001_initial.sql` 与启动建表口径一致；`backend/scripts/` 含 seed 与演示输入导出。

环境变量：`COMPOSE_PROJECT_NAME` 短名，`FRONTEND_PORT/BACKEND_PORT/DB_PORT` 宿主端口，`DB_PASSWORD` 数据库密码，`JWT_SECRET` JWT密钥，`SEED_DEMO` 演示seed开关。容器内部 `DATABASE_URL/REDIS_URL/TASK_MODE/ARTIFACT_DIR` 由 Compose 注入；`TASK_MODE=redis` 是容器工作模式。

共享枚举：

| 枚举 | Python 定义与使用 | TypeScript 定义与使用 |
|---|---|---|
| Role | `src/constants/enums.py`，`services/auth.py` 鉴权 | `src/types/entities.ts` User.role、`constants/enums.ts` roles、`App.tsx` |
| RunStatus | `constants/enums.py`，`models/entities.py` 默认状态，`services/run.py` 迁移 | `types/entities.ts` Run.status、`constants/enums.ts` runStatus、`StatusBadge.tsx` |
| ReviewStatus | `constants/enums.py`、`models/entities.py`、`services/review.py` | `types/entities.ts` Review.status、`constants/enums.ts` reviewStatus、`StatusBadge.tsx` |
| SupplementStatus | `constants/enums.py`、`services/dataset.py` 补报落库状态 | `types/entities.ts` Supplement.status、`constants/enums.ts` supplementStatus |

## 验收与已知差异

真实结果见批次 `test-artifacts/gb-2101/TESTING.md`；测试脚本与截图不放源码内。标准库 Docker 主流程脚本在 `test-artifacts/gb-2101/tests/docker_acceptance.py`，默认 BASE_URL 为后端19200；截图脚本 `screenshots.cjs` 需要独立QA环境可用的 Playwright。

本轮环境拒绝 Docker socket、浏览器进程无法启动，因此容器健康与真实页面截图尚未完成，状态为 partial。已执行的本地 API/算法测试使用 SQLite/inline，覆盖补报四种判定、幂等重投、失效传导、重算版本绑定与计算途中失效竞态；React18 依赖已可安装，`tsc --noEmit && vite build` 在交付的 React18 要求下通过，但不代表 Docker 镜像构建通过。

数据库按实体分别建表、以 TEXT JSON 保存字段；应用层校验引用，未配置数据库外键和逐字段索引，适用于演示规模。Redis 简单队列没有任务租约和崩溃重放；worker 崩溃后需重新提交未完成任务。未实现外部邮件分发或定时发送，本题聚焦试验分析与复核交接。

## License

MIT，见 LICENSE。
