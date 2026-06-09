# STEP 模型分析 Word 报告生成器 Spec

## Why
用户有 11 个铁方通相关的 STEP 零件文件，需要一个 Python 脚本自动解析每个 STEP 文件，提取尽可能全面的模型信息，并生成对应的 Word 报告文档。

## What Changes
- 新建 Python 脚本，使用 pythonOCC 解析 STEP 文件
- 提取模型的全面信息（拓扑、几何、尺寸、孔特征、壁厚等）
- 自动识别模型类型（管状/方通/通用机械零件）
- 使用 python-docx 为每个 STEP 文件生成独立的 Word 报告
- 报告包含结构化表格、关键参数汇总

## Impact
- Affected code: 新建脚本文件 `step_analyzer.py`
- 依赖: pythonOCC (OCP), python-docx, openpyxl

## ADDED Requirements

### Requirement: STEP 文件解析
系统 SHALL 使用 pythonOCC 读取 STEP 文件，并提取以下信息：

1. **基本拓扑信息**
   - 顶点数(Vertex)、边数(Edge)、线数(Wire)、面数(Face)、壳数(Shell)、体数(Solid)

2. **几何类型统计**
   - 各类面类型数量（平面、圆柱面、圆锥面、球面、环面、B样条面等）
   - 各类边曲线类型数量（直线、圆弧、椭圆、B样条曲线等）

3. **尺寸信息**
   - 整体边界框(BoundingBox)：X/Y/Z 方向尺寸
   - 体积(Volume)
   - 表面积(Surface Area)
   - 质心(Center of Mass)

4. **孔特征分析**
   - 孔洞面识别（圆柱面/圆锥面 + 内Wire判断）
   - 规则孔 vs 不规则孔分类
   - 孔的参数：半径/直径、轴线位置、轴线方向
   - 孔数量统计

5. **管状/方通结构分析**（自动检测）
   - 同轴圆柱面配对识别管状结构
   - 管长、外径、内径、壁厚
   - 方通空心结构检测（相对的平行平面配对）
   - 截面尺寸

6. **壁厚分析**
   - 管状结构：外径 - 内径
   - 通用壁厚：内外表面最小距离法

### Requirement: 模型类型自动识别
系统 SHALL 根据提取的几何特征自动判断模型类型：
- **管状零件**：存在同轴内外圆柱面
- **方通零件**：存在多组平行平面且内部有空心结构
- **通用机械零件**：以上特征均不显著

### Requirement: Word 报告生成
系统 SHALL 为每个 STEP 文件生成独立的 Word 文档，包含以下章节：

1. **概览**：文件名、模型类型、基本描述
2. **拓扑信息**：顶点/边/线/面/壳/体数量表格
3. **几何类型分布**：面类型统计表、边类型统计表
4. **尺寸信息**：边界框尺寸、体积、表面积、质心
5. **孔特征**：孔数量、规则/不规则分类、各孔参数表
6. **管状/方通结构**（如检测到）：管长、外径、内径、壁厚、截面尺寸
7. **壁厚信息**：各测量点的壁厚数据

报告格式要求：
- 使用结构化表格呈现数据
- 标题层级清晰
- 数值保留合理精度（长度3位小数mm，体积2位小数）
- 文件名格式：`{原STEP文件名}_分析报告.docx`

### Requirement: 批量处理
系统 SHALL 支持批量处理指定目录下所有 STEP 文件，每个文件独立生成 Word 报告。

### Requirement: 命令行接口
系统 SHALL 提供命令行接口：
```
python step_analyzer.py --input <STEP文件或目录> [--output <输出目录>]
```
- `--input`：单个 STEP 文件路径或包含 STEP 文件的目录
- `--output`：Word 文件输出目录，默认为输入文件同目录

#### Scenario: 处理单个文件
- **WHEN** 用户执行 `python step_analyzer.py --input /path/to/file.STEP`
- **THEN** 在同目录生成 `file_分析报告.docx`

#### Scenario: 批量处理目录
- **WHEN** 用户执行 `python step_analyzer.py --input /path/to/step_files/ --output /path/to/output/`
- **THEN** 对目录下所有 .step/.stp 文件逐一生成 Word 报告到输出目录

#### Scenario: 文件读取失败
- **WHEN** STEP 文件无法读取或格式错误
- **THEN** 打印错误信息并跳过该文件，继续处理其他文件
