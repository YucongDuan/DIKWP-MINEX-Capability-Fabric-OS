# DIKWP MINEX Capability Fabric OS v1.0.0

## 中文：三分钟开始

### 直接使用

双击打开：

```text
DIKWP_MINEX_CAPABILITY_FABRIC_OS_v1.0.0.html
```

1. 写出想得到的结果，而不是先指定 App。
2. 检查已有语义输入、目标输出、授权范围和硬约束。
3. 运行规划器，查看 Pareto 路线及被拒绝原因。
4. 本地内置能力可执行；API、GUI、跨设备和市场路线在参考内核中保持适配或提案状态。
5. 导出计划收据，或用 Python 版本执行并形成结果收据。

### Python 单文件程序

```bash
python DIKWP_MINEX_CAPABILITY_FABRIC_OS_v1.0.0.pyz \
  demo --workspace .minex-demo --reset
```

### 核心边界

```text
自动外部行动权限 = 0
自动付款权限 = 0
自动签约权限 = 0
自动发布权限 = 0
```

“最小耗费”必须先满足权限、质量、隐私、可逆性和结果验证；不同单位的耗费不得静默压成一个伪客观总量。

---

## English: three-minute start

### Direct use

Open:

```text
DIKWP_MINEX_CAPABILITY_FABRIC_OS_v1.0.0.html
```

1. Declare the outcome instead of naming an application first.
2. Review semantic inputs, required outputs, granted scopes, and hard constraints.
3. Run the planner and inspect the Pareto routes and rejection reasons.
4. Registered local builtins can execute; API, GUI, peer, and market paths remain adapter-backed or proposal-only in the reference core.
5. Export a plan receipt, or use the Python distribution to execute a local route and generate an outcome receipt.

### Standalone Python program

```bash
python DIKWP_MINEX_CAPABILITY_FABRIC_OS_v1.0.0.pyz \
  demo --workspace .minex-demo --reset
```

### Constitutional boundary

```text
automatic external-action authority = 0
automatic payment authority = 0
automatic contract authority = 0
automatic publication authority = 0
```

Minimum expenditure is optimized only after authority, quality, privacy, reversibility, and result-verification gates pass. Costs with different units remain separately visible.
