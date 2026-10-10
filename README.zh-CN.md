# NiAsymCoupling v2.0.0 文献数据公开派生版

[English](README.md)

这是由本项目指定的冻结 v2 派生的文献数据包，包含文献结果行、分子结构、反应条件、选择性标签、来源定位及质量标记。主范围为文献报告的镍催化 C(sp²)–C(sp³) 成键；范围外与范围待核实的记录保留在档案集合。

**[下载 v2.0.0 完整数据包](https://github.com/EthanTang2005/NiAsymCoupling/releases/download/v2.0.0/NiAsymCoupling-v2.0.0.zip)** · [ZIP SHA-256 校验文件](https://github.com/EthanTang2005/NiAsymCoupling/releases/download/v2.0.0/NiAsymCoupling-v2.0.0.zip.sha256)

版本 **2.0.0**，发布包准备日期 **2026-10-10**，目标仓库为 [EthanTang2005/NiAsymCoupling](https://github.com/EthanTang2005/NiAsymCoupling)。完整数据包包含 SQLite、7 个 CSV 和配套代码/文档。GitHub 自动提供的 **Source code (zip/tar.gz)** 仅含仓库文件，不包含数据包。

`scripts/`、`examples/` 与 `schema.sql` 的原创代码采用 MIT；CC BY 4.0 仅适用于整理者实际控制的原创文档、整理/注释与汇编权利。它们不重新许可第三方受保护材料，也不为事实增加新的限制。已核查的上游条款与仍未核实的适用性分别保留，见 [LICENSING.md](LICENSING.md) 和 [第三方说明](THIRD_PARTY_NOTICES.md)。未声明数据 DOI 或关联发表论文。

源数据库内部版本为 **1.4.66**，日期 **2026-10-07**，SHA-256 为 `ada489cddda9bb948f044e0a558df82de5a4eb2340b1910c07a04606fab07c9d`。本包采用简化的公开 schema，**不等于完整冻结 v2**。36 条本地实验及其仅属于本地的数据集、来源和分子被排除，冻结源未修改。

| 统计口径 | 数量 |
|---|---:|
| 文献来源结果行，总档案 | 7,935 |
| 主范围结果行 | 4,596 |
| 主范围中数值 ee 结果行 | 4,416 |
| 其他范围与范围待核实档案行 | 3,339 |
| 主范围数值 ee＋必要底物结构完整＋配体 SMILES 非空 | 3,608 |
| 作者数据表来源观察，单独存储 | 6,567 |
| 关联文献 / 数据集 / 分子实体 | 137 / 34 / 6,080 |

统计单位为**来源结果行**，并非已证明相互独立的物理实验。作者原表观察不能与结果行相加；数据集成员关系可能重叠。必要底物结构完整是原 v2 视图的状态，不代表本轮独立逐条复核了原始 SI，更不等于配体、条件、标签及去重全部通过。

下载并解压上述 **NiAsymCoupling-v2.0.0.zip** 后，进入 `NiAsymCoupling-v2.0.0/` 文件夹，即可使用其中的 `data/NiAsymCoupling_v2_public.sqlite` 或 `data/records.csv`。如果先 clone 仓库，请将数据包解压目录的**内容**合并到仓库根目录，使 `data/`、`scripts/`、`examples/` 和 `manifest.json` 位于同一层；仅 clone 仓库没有数据库。ZIP 的 `.sha256` 文件用于校验完整下载，解压后的 `SHA256SUMS` 用于校验逐个文件。

CSV 中 `in_main_scope=1` 对应主范围。公开数据库保留规范化的质量标记、底物角色状态、原作者观察和来源值变体；完整定义见 [数据字典](docs/DATA_DICTIONARY.md)。

```bash
python3 -B examples/query.py
python3 -B scripts/verify_public.py
```

Python 3.11+ 即可，不需要额外 Python 依赖。维护者持有指定冻结源时，可通过 `scripts/build_public.py --source ... --output ...` 在新目录复现数据；脚本强制核对 SHA、只读源库，并拒绝覆盖已有目标数据库。仓库文档与许可说明独立维护，不属于数据库重建输出。

ee 正负号按来源保留，不能跨来源直接解释为同一 R/S 构型；100% ee 不适合直接计算有限对数能量差；缺失温度与室温文字没有被擅自换成 25°C。具体限制见 [KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md)。引用时应保留本包版本和校验和，同时引用实际使用记录对应的原始文献及数据提供者。

本版本引用信息见 [CITATION.cff](CITATION.cff)：Yichen Tang，NiAsymCoupling: literature-only public derivative，2.0.0，2026-10-10。仓库不能独立从原始 SI 重建全部冻结库；持有同一 SHA-256 私有冻结 v2 的维护者可复现公开投影，普通使用者可直接查询并验证已下载的数据包。
