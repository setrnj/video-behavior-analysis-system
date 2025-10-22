# 视频行为分析 — RFM 用户价值分群系统

一个用于基于视频行为数据进行用户价值分群（RFM：Recency, Frequency, Monetary）的 Python 项目。适用于视频/流媒体/短视频平台，通过用户观看行为与/或消费数据计算 R、F、M 指标、打分并划分分群，帮助运营与产品做精准运营、召回与激励策略。

目录
----
- 项目简介
- 快速开始
- 数据说明（输入/输出）
- RFM 计算与打分细节
- 分群策略与示例
- 配置文件说明（YAML）
- CLI 与 API 使用示例
- 可视化与分析报告
- 测试、部署与生产化建议
- 项目结构（参考)
- 贡献与许可证
- 联系方式

项目简介
----
目标：
- 从视频行为日志中提取用户层面的 R、F、M 指标
- 提供灵活的打分与分群策略（分位数 / 自定义阈值 / 权重）
- 输出可用于后续运营的分群标签与统计报告

适用场景：
- 日活/周活用户分群
- 召回目标用户识别（如 At-Risk）
- 付费/消费用户分析（如付费路径分析）
- 内容/渠道/���域维度的分群对比

快速开始
----
1. 克隆仓库
```bash
git clone https://github.com/setrnj/video-behavior-analysis-system.git
cd video-behavior-analysis-system
```

2. 创建虚拟环境并安装依赖
```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```
如果仓库没有 requirements.txt，可先安装常用库：
```bash
pip install pandas numpy scikit-learn pyyaml matplotlib seaborn jupyterlab
```

3. 准备数据（CSV / Parquet / DB）
按下文“数据说明”准备输入文件。

4. 运行（示例，脚本名按仓库实际文件替换）
```bash
python run_rfm.py --config config/rfm_config.yaml
```
或
```bash
python scripts/compute_rfm.py --input data/behaviors.csv --output results/segments.csv
```

数据说明（输入）
----
最小行为表字段（示例）：
- user_id (string) — 用户唯一标识
- event_time (string / timestamp) — 行为时间（ISO 格式推荐：YYYY-MM-DDTHH:MM:SS）
- watch_duration (float) — 观看时长（秒或分钟，请在 config 指定单位）
- amount (float, optional) — 消费金额（用于 M 指标，如无可用 watch_duration 替代）

示例 CSV:
```csv
user_id,event_time,watch_duration,amount,content_id
u001,2025-10-20T12:00:00,120,0.0,vid_1001
u002,2025-10-21T08:30:00,300,5.0,vid_2001
```

输出文件（常见）
- results/rfm_table.csv — 每用户的 R、F、M 原始值与分数
- results/segments.csv — user_id + r_score/f_score/m_score + rfm_score + segment
- results/figures/ — 常见统计图（RFM 分布、segment 人数、Top N 用户）

RFM 计算与打分（细节）
----
基础指标定义：
- Recency（R） = 参考日期 - 用户最后一次行为时间（以天/小时计）
- Frequency（F） = 在统计窗口内的行为次数 / 会话数 / 有效观看天数（按需求）
- Monetary（M） = 消费金额总和 或 观看时长总和（在无消费数据时推荐使用“观看时长”）

常见聚合：
- frequency_agg: count / unique_days / sum(session_count)
- monetary_agg: sum(amount) / sum(watch_duration)

打分方法（示例）
1. Quantile（分位数）打分（按 R 降序或升序注意方向）：
   - 将各指标按分位数切分为 1-5 分（或 1-3 分）
   - Recency：最近越近分数越高（小值 -> 高分），需对 R 做反向处理
2. 自定义阈值：
   - 业务定义阈值区间并映射到分数
3. 加权合成：
   - rfm_score = w_r * r_score + w_f * f_score + w_m * m_score
   - 或组合成字符串 "RFM"（例如 5-4-3），并用映射表到 segment 名称

示例：Quantile 案例（伪代码）
```text
# 假设分为 5 档量表
r_score = 6 - quantile_rank(recency)   # 如果 quantile_rank 1 表示最小 recency
f_score = quantile_rank(frequency)
m_score = quantile_rank(monetary)
rfm_value = r_score * 100 + f_score * 10 + m_score
```

分群策略示例（映射）
----
常见分群（你可以按业务自定义）：
- Champions（冠军）: R>=4, F>=4, M>=4
- Loyal（忠诚）: F>=4, M>=3
- Potential（潜力）: R>=3, F>=3
- At Risk（流失风险）: R<=2, F<=2
- Lost（流失）: R==1, F==1, M==1

示例映射表（CSV / YAML）可以在 config 中定义，便于运营调整。

配置文件（config/rfm_config.yaml）详解
----
示例：
```yaml
data:
  input_path: "data/behaviors.csv"
  format: "csv"                # csv / parquet / db
  time_column: "event_time"
  user_column: "user_id"
  duration_column: "watch_duration"
  amount_column: "amount"      # 可为空

rfm:
  reference_date: "2025-10-22" # 用于 recency 计算的参考日期
  recency_unit: "days"         # days / hours
  frequency_method: "count"    # count / unique_days / sessions
  monetary_method: "sum"       # sum / avg
  lookback_days: 90            # 统计窗口长度（如计算 frequency)

scoring:
  method: "quantile"           # quantile / custom
  quantiles: [0.2, 0.4, 0.6, 0.8]  # 切分为 5 档
  custom_thresholds:            # method=custom 时使用
    recency: [7, 14, 30, 90]
    frequency: [1, 3, 7, 15]
    monetary: [0, 5, 20, 100]
  weights:
    r: 0.4
    f: 0.3
    m: 0.3

output:
  rfm_table: "results/rfm_table.csv"
  segments: "results/segments.csv"
  figures_dir: "results/figures"
  save_plots: true
```

CLI 使用示例
----
基础运行：
```bash
python run_rfm.py --config config/rfm_config.yaml
```
按文件输入输出：
```bash
python scripts/compute_rfm.py --input data/behaviors.csv --output results/segments.csv --ref-date 2025-10-22
```
常见选项解释：
- --config: 指定 YAML 配置
- --input/--output: 覆盖配置文件里的路径
- --ref-date: 运行时覆盖参考日期（方便回溯计算)
- --dry-run: 仅输出统计信息不保存文件

API 使用示例（Python）
----
以下为示例用法，实际类/函数名请按仓库代码调整：
```python
from src.rfm import RFMAnalyzer
import yaml

cfg = yaml.safe_load(open("config/rfm_config.yaml"))
analyzer = RFMAnalyzer(cfg)
# 返回 DataFrame: user_id, recency, frequency, monetary, r_score, f_score, m_score
rfm_df = analyzer.run()
rfm_df.to_csv("results/rfm_table.csv", index=False)
segments = analyzer.segment(rfm_df)  # 返回含 segment 列的 DataFrame
segments.to_csv("results/segments.csv", index=False)
```

可视化（建议）
----
推荐生成以下图表以辅助运营决策：
- R/F/M 单变量分布（直方图/箱线图）
- RFM 三维热力图（或分段柱状图）
- 各 segment 人数占比饼图
- 各 segment 的核心指标对比（平均观看时长、留存、付费率）

可用 matplotlib / seaborn / plotly 保存到 results/figures。

数据校验 & 单元测试
----
- 建议在数据读入阶段做 schema 校验（字段是否存在、时间格式、数值范围）
- 单元测试覆盖：
  - 指标聚合逻辑（recency/frequency/monetary）
  - 打分逻辑（quantile 与 custom 映射）
  - 分群映射（segment mapping）
使用 pytest 编写测试，数据可以放在 tests/fixtures。

生产化与部署建议
----
- 定期任务：用 Airflow/cron 定时触发（每日或每周），并把结果写入 BI 数据库或推送给 downstream 服务
- 容器化：提供 Dockerfile，将脚本、依赖、配置一并打包
- 日志与监控：记录每次运行的样本数、异常用户数、耗时
- 版本管理：对算法变更做 versioned 输出（例如 results/v1.0/segments.csv），以便对比

示例 Dockerfile（参考）
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "run_rfm.py", "--config", "config/rfm_config.yaml"]
```

项目结构（推荐/参考）
----
- config/                # YAML 配置
- data/                  # 示例数据
- src/                   # 核心实现（读取、特征工程、分群、可视化）
- scripts/               # 可执行脚本 / CLI
- notebooks/             # 分析笔记本
- results/               # 输出结果（csv / figures）
- tests/                 # 单元测试
- requirements.txt
- README.md

常见问题（FAQ）
----
Q: 没有 amount 字段怎么办？  
A: 使用观看时长（watch_duration）替代 M，或用观看次数 * 平均价值估算。

Q: R、F、M 各自区间如何选择？  
A: 可用 quantile 自动切分；也可与业务方沟通采用自定义阈值，优先考虑业务可解释性。

Q: 如何验证分群效果？  
A: 结合后续行为（如 7/30 天留存、付费转化）对比不同 segment 的 KPI，评估分群是否能区分用户价值。

贡献
----
欢迎提交 issue/PR：
1. Fork 本仓库
2. 新建分支：git checkout -b feature/your-feature
3. 提交代码并发起 PR（描述变更与测试）
4. 添加/更新 tests

许可证
----
建议使用 MIT 许可证。请根据项目需要替换为合适的许可证文件 LICENSE。

联系方式
----
作者: setrnj  
仓库地址: https://github.com/setrnj/video-behavior-analysis-system

附录：示例流程（端到端）
----
1. 准备行为日志 data/behaviors.csv
2. 配置 config/rfm_config.yaml（指定时间列、user 列、参考日期等）
3. 运行脚本生成 rfm_table 与 segments
4. 检查 results/figures 中的可视化报告
5. 将结果接入 BI 或导出到数据库供运营使用
