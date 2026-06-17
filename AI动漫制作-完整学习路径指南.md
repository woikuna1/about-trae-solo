# AI动漫制作 — 完整学习路径指南

> 适用对象：零基础入门，目标是制作AI动漫短视频/动画片段
> 风格覆盖：日系二次元、国风/国漫、3D动漫风
> 推荐模型版本：**SDXL**（质量高、生态成熟）

---

## 目录

- [全流程管线概览](#全流程管线概览)
- [第1步：学会用SD/ComfyUI生成单张动漫图](#第1步学会用sdcomfyui生成单张动漫图)
- [第2步：学会ControlNet控制姿态和构图](#第2步学会controlnet控制姿态和构图)
- [第3步：学会LoRA训练，保持角色一致](#第3步学会lora训练保持角色一致)
- [第4步：学会I2V视频生成](#第4步学会i2v视频生成)
- [第5步：学会后期合成](#第5步学会后期合成)
- [第6步：串联完整工作流](#第6步串联完整工作流)
- [附录：工具官网与资源汇总](#附录工具官网与资源汇总)

---

## 全流程管线概览

AI动漫制作分为5大阶段：

```
1. 剧本/分镜  →  AI辅助编剧 → 分镜脚本 → 场景描述 → Prompt工程
2. 角色设计    →  角色立绘 → LoRA训练 → 角色一致性 → 表情/姿态变体
3. 场景生成    →  背景图 → 风格统一 → 多角度场景 → 场景分层
4. 动画生成    →  图生视频(I2V) → 动作控制 → 口型同步 → 镜头运动
5. 后期合成    →  配音/音效 → 字幕 → 特效 → 剪辑 → 调色
```

**四大核心挑战：**
- **角色一致性** — 同一角色在不同场景/姿态中保持外观一致
- **风格统一** — 全片保持统一的美术风格
- **动作可控** — 精确控制角色动作和镜头运动
- **时序连贯** — 相邻帧/镜头之间的视觉连贯性

---

## 第1步：学会用SD/ComfyUI生成单张动漫图

### 1.1 理解Stable Diffusion

**SD是什么：** Stable Diffusion是一个开源的AI图像生成模型，你给它文字描述，它生成对应图片。

**工作原理（扩散模型）：**
1. 训练时：清晰图片 → 逐步加噪 → 纯噪声（模型学习噪声规律）
2. 生成时：纯噪声 → 逐步去噪（20-30步）→ 清晰图片
3. 你的文字描述像导航，告诉模型"往哪个方向去噪"

**SD在AI动漫中的作用：**
- 角色立绘生成
- 场景背景生成
- 分镜画面生成
- 角色变体（不同表情/姿态/服装）
- 风格统一（通过LoRA/Checkpoint控制）
- 动画基础帧（为视频生成提供起始画面）

**版本选择：**

| 版本 | 分辨率 | 特点 | 推荐度 |
|------|--------|------|--------|
| SD 1.5 | 512×512 | 最老，插件最多，画质落后 | 入门可用 |
| **SDXL** | **1024×1024** | **质量高，生态成熟** | **推荐首选** |
| SD 3.0/3.5 | 1024×1024 | 新架构，质量好但生态不成熟 | 观望 |
| Flux | 可变 | 质量极高，生态增长中 | 进阶选择 |

> **零基础入门推荐SDXL**：质量够高，动漫模型生态丰富（Animagine XL、Counterfeit XL等），社区教程多。

**相关资源：**
- Stability AI 官网：https://stability.ai
- SD 原始仓库：https://github.com/CompVis/stable-diffusion
- SD V2+ 仓库：https://github.com/Stability-AI/StableDiffusion
- Hugging Face（模型托管）：https://huggingface.co
- Civitai（模型分享社区）：https://civitai.com

---

### 1.2 SD的界面选择：WebUI vs ComfyUI

SD本身只是一个模型（代码），你需要一个**界面**来操作它。主流选择有两个：

#### Automatic1111 WebUI（简称A1111）

- **形态：** 传统表单式界面，填参数→点生成→出图
- **优点：**
  - 上手简单，像填表一样操作
  - 插件生态丰富，安装方便
  - 适合初学者理解SD的基本概念
- **缺点：**
  - 复杂工作流难以搭建
  - 不支持节点式流程编排
  - 批量处理不够灵活

#### ComfyUI

- **形态：** 节点式界面，像搭积木一样连接各个功能模块
- **优点：**
  - 工作流可保存、分享、复用
  - 可以串联复杂的多步骤流程（绘图→ControlNet→AnimateDiff一条龙）
  - 社区有大量现成工作流模板
  - 支持批处理，效率高
  - **是AI动漫制作的核心平台**
- **缺点：**
  - 学习曲线陡峭，初看界面会懵
  - 节点连线出错时调试麻烦

#### 学习建议

```
阶段一：先用A1111或在线服务理解SD基本概念（1-2周）
阶段二：转入ComfyUI，学习节点式操作（2-4周）
阶段三：在ComfyUI中搭建完整动漫工作流（持续）
```

> **做动漫最终必须用ComfyUI**，因为AnimateDiff、ControlNet串联等复杂流程只有ComfyUI能高效完成。但不必一开始就上ComfyUI，先理解概念再转。

**相关资源：**
- A1111 WebUI：https://github.com/AUTOMATIC1111/stable-diffusion-webui
- ComfyUI：https://github.com/comfyanonymous/ComfyUI
- ComfyUI 中文教程：在B站搜索"ComfyUI 教程"

---

### 1.3 核心概念详解

#### Checkpoint（大模型/底模）

**是什么：** SD的主模型文件（通常2-7GB），决定了生成图片的整体画风和质量。

**类比理解：** Checkpoint就像"画师的画风基础"——一个学过日系动漫的画师和一个学过油画的画师，画出来的东西天然不同。

**动漫常用Checkpoint：**

| Checkpoint | 风格 | 适用 |
|-----------|------|------|
| Animagine XL | 日系二次元，高质量 | SDXL首选 |
| Counterfeit XL | 日系，色彩鲜明 | 通用动漫 |
| DreamShaper XL | 写实+动漫混合 | 多风格 |
| 国风3 XL | 中国风 | 国风/国漫 |
| Disney Pixar XL | 3D动画风 | 3D动漫 |

**去哪下载：** Civitai（https://civitai.com）是最大的模型分享社区，搜索Checkpoint类型即可。

#### VAE（变分自编码器）

**是什么：** 负责图片的"解码"——把SD内部的潜空间表示转换为肉眼可见的图片。

**类比理解：** SD生成图片时先在"压缩空间"里工作（潜空间），VAE负责"解压缩"成真实图片。没有VAE，生成的图片会发灰/偏色。

**关键点：**
- 有些Checkpoint自带VAE，不需要额外加载
- 如果出图发灰，通常就是VAE没加载
- 动漫常用VAE：`kl-f8-anime2`、`sdxl_vae.safetensors`

#### Sampler（采样器）

**是什么：** 决定"去噪"的数学算法，影响生成质量和速度。

**动漫常用采样器：**

| 采样器 | 特点 |
|--------|------|
| DPM++ 2M Karras | **最推荐**，质量高、速度快、细节好 |
| Euler a | 简单快速，适合探索性生成 |
| DPM++ SDE Karras | 质量最高但速度慢 |
| DDIM | 老牌经典，适合Img2Img |

#### CFG Scale（提示词相关性）

**是什么：** 控制AI对Prompt的遵从程度。

- **数值低（3-5）：** AI更自由发挥，画面可能偏离描述但更自然
- **数值中等（7-12）：** 平衡状态，**动漫常用7-9**
- **数值高（15-30）：** 严格遵从Prompt，但画面可能过饱和/不自然

#### Steps（迭代步数）

**是什么：** 去噪的步数，步数越多画面越精细，但边际递减。

- **15-20步：** 快速预览
- **20-30步：** **动漫常用范围**，质量与速度平衡
- **40+步：** 通常没必要，质量提升微小

#### Seed（种子）

**是什么：** 随机数种子，决定了初始噪声的图案。

- 相同Seed + 相同参数 = 生成完全相同的图片
- 改变Seed = 生成不同构图但风格相似的图片
- 用 `-1` 表示随机种子

---

### 1.4 学会写Prompt（提示词）

Prompt是你和SD沟通的语言，写好Prompt是AI绘图的核心技能。

#### Prompt的基本结构

```
[质量词], [主体描述], [动作/表情], [服装/配饰], [场景/背景], [风格词], [其他修饰]
```

#### 质量词（放在最前面，权重最高）

```
masterpiece, best quality, very aesthetic, absurdres, highres
```

#### 主体描述

```
1girl, blue hair, long hair, blue eyes, school uniform
```

#### 动作/表情

```
smiling, looking at viewer, standing, arms behind back
```

#### 场景/背景

```
classroom, afternoon sunlight, window, cherry blossoms outside
```

#### 风格词

```
anime style, cel shading, vibrant colors, makoto shinkai style
```

#### 权重语法

```
(masterpiece:1.2)        # 强调，1.2倍权重
(anime style:1.3)        # 更强强调
(blurry:0.5)             # 弱化，0.5倍权重
[bad anatomy]            # 方括号弱化
```

#### 负面Prompt（Negative Prompt）

指定**不要出现**的内容：

```
worst quality, low quality, bad anatomy, bad hands, missing fingers,
extra digits, cropped, watermark, signature, deformed
```

#### 不同风格的Prompt关键词

**日系精致风：**
```
makoto shinkai style, kyoani style, detailed background,
vibrant colors, cinematic lighting, lens flare
```

**国风/国漫：**
```
chinese ink painting, watercolor style, oriental fantasy,
traditional chinese clothes, ink wash, flowing robes
```

**吉卜力风：**
```
studio ghibli style, miyazaki style, ghibli background,
warm colors, hand-drawn, whimsical
```

**3D动漫风：**
```
3d render, pixar style, disney style, smooth shading,
subsurface scattering, volumetric lighting
```

---

### 1.5 动手生成第一张动漫图

#### 方式一：在线服务（零门槛）

不需要本地显卡，直接在网页上使用：

| 服务 | 网址 | 特点 |
|------|------|------|
| Civitai 在线生成 | https://civitai.com | 免费额度，直接用社区模型 |
| Tensor.Art | https://tensor.art | 免费额度多，支持ComfyUI工作流 |
| Hugging Face Spaces | https://huggingface.co/spaces | 免费体验各种SD模型 |

#### 方式二：云端GPU（推荐入门）

| 平台 | 网址 | 特点 |
|------|------|------|
| AutoDL | https://www.autodl.com | 国内最便宜，按小时计费，预装SD环境 |
| RunPod | https://runpod.io | 海外平台，按小时计费 |
| Google Colab | https://colab.research.google.com | 免费GPU，但有时间限制 |

#### 方式三：本地部署（需要NVIDIA显卡）

**最低配置：** RTX 3060 12GB

**安装步骤（A1111 WebUI）：**
1. 安装Python 3.10和Git
2. 克隆仓库：`git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui`
3. 运行 `webui-user.bat`（Windows）或 `webui.sh`（Linux）
4. 等待自动安装依赖
5. 下载SDXL动漫Checkpoint放入 `models/Stable-diffusion/`
6. 打开浏览器访问 `http://localhost:7860`

**安装步骤（ComfyUI）：**
1. 克隆仓库：`git clone https://github.com/comfyanonymous/ComfyUI`
2. 安装依赖：`pip install -r requirements.txt`
3. 下载Checkpoint放入 `models/checkpoints/`
4. 运行 `python main.py`
5. 打开浏览器访问 `http://localhost:8188`

#### 第一次生成的建议Prompt

**正面Prompt：**
```
masterpiece, best quality, 1girl, silver hair, long hair,
blue eyes, school uniform, smiling, standing, cherry blossoms,
afternoon sunlight, anime style, detailed background
```

**负面Prompt：**
```
worst quality, low quality, bad anatomy, bad hands,
missing fingers, extra digits, watermark, signature
```

**参数设置：**
- Checkpoint: Animagine XL 或 Counterfeit XL
- Sampler: DPM++ 2M Karras
- Steps: 25
- CFG Scale: 7
- Size: 1024×1024
- Seed: -1（随机）

---

## 第2步：学会ControlNet控制姿态和构图

### 2.1 ControlNet是什么

**一句话解释：** ControlNet让你用"参考图"精确控制SD生成的构图、姿态、线稿等，而不是纯靠文字描述碰运气。

**为什么需要ControlNet：**
- 纯文字Prompt很难精确控制角色姿态（"左手举起来"AI可能理解错）
- 构图难以精确控制（"人物在画面左侧1/3处"很难用文字描述）
- 多角色场景中无法分别控制每个人

**ControlNet的工作原理：**
1. 你提供一张参考图（如骨骼图、线稿、深度图）
2. ControlNet从参考图中提取结构信息
3. SD在生成时遵循这些结构约束，同时填充细节和风格

**相关资源：**
- ControlNet GitHub：https://github.com/lllyasviel/ControlNet

### 2.2 ControlNet的主要类型

| 类型 | 输入 | 用途 | 动漫使用频率 |
|------|------|------|-------------|
| **OpenPose** | 骨骼姿态图 | 控制角色动作姿态 | ★★★★★ |
| **Depth** | 深度图 | 控制空间前后关系 | ★★★★ |
| **Canny** | 边缘线稿 | 保持轮廓精确 | ★★★★ |
| **Lineart** | 线稿图 | 按线稿上色 | ★★★ |
| **Scribble** | 涂鸦草图 | 粗略控制构图 | ★★★ |
| **Softedge** | 柔和边缘 | 类似Canny但更柔和 | ★★ |
| **Seg** | 语义分割图 | 指定区域内容 | ★★ |
| **IP-Adapter** | 参考图片 | 保持面部/风格一致 | ★★★★★ |
| **InstantID** | 单张人脸照 | 面部一致性最强 | ★★★★ |

### 2.3 动漫中最常用的ControlNet组合

**角色姿态控制：**
```
OpenPose（指定骨骼动作）+ Depth（控制空间关系）
```

**角色面部一致性：**
```
IP-Adapter（参考角色面部）+ OpenPose（控制姿态）
```

**场景构图控制：**
```
Depth（空间深度）+ Canny（边缘轮廓）
```

**线稿上色：**
```
Lineart（输入线稿）+ 风格Prompt
```

### 2.4 DWPose — 更精准的骨骼检测

**是什么：** OpenPose的升级版，检测更精准（包括手指、面部表情）。

**用途：** 从真人视频/图片中提取骨骼，用于控制动漫角色做出相同动作。

**相关资源：** ComfyUI中安装 `comfyui_controlnet_aux` 节点即可使用。

### 2.5 学习要点

1. 学会在ComfyUI中加载ControlNet模型
2. 理解不同ControlNet类型的适用场景
3. 掌握ControlNet权重调节（0.3-1.0，越高越严格遵循参考）
4. 学会组合多个ControlNet同时使用
5. 学会从真人/3D模型提取骨骼参考图

**相关资源：**
- IP-Adapter：https://github.com/tencent-ailab/IP-Adapter
- InstantID：https://github.com/InstantID/InstantID

---

## 第3步：学会LoRA训练，保持角色一致

### 3.1 LoRA是什么

**一句话解释：** LoRA（Low-Rank Adaptation）是一个轻量级的模型附加层，让SD"记住"特定角色/风格，生成时保持一致。

**类比理解：** 如果Checkpoint是"画师的基础画风"，LoRA就是"画师参考了某个角色的设定集后，学会了画这个角色"。

**LoRA vs 全量微调：**

| 特性 | LoRA | 全量微调（Fine-tuning） |
|------|------|----------------------|
| 训练参数量 | 极少（2-150MB） | 全部（几GB） |
| 训练时间 | 几小时 | 几天 |
| 显存需求 | 8-12GB | 24GB+ |
| 效果 | 角色一致性够用 | 最强但容易过拟合 |
| 灵活性 | 可叠加多个LoRA | 一次只能一个模型 |

### 3.2 LoRA训练完整流程

#### 第一步：素材准备

- 收集 **20-50张** 角色图片
- 不同角度（正面、侧面、3/4侧面）
- 不同表情（微笑、严肃、惊讶等）
- 不同服装（如有需要）
- 背景尽量简洁，角色清晰
- 分辨率建议 512×512 或 1024×1024

#### 第二步：打标签（Captioning）

为每张图片写描述性标签，告诉AI"这张图里有什么"。

**自动打标工具：**
- **WD14 Tagger** — 最常用，自动生成动漫风格标签
  - GitHub：https://github.com/toriato/stable-diffusion-webui-wd14-tagger
- **BLIP** — 生成自然语言描述

**标签原则：**
- 描述角色的固定特征（发色、瞳色、发型等）
- 不要描述可变特征（特定表情、特定动作）——这些让Prompt控制
- 格式示例：`1girl, silver hair, long hair, blue eyes, school uniform, simple background`

#### 第三步：训练

**训练工具：**

| 工具 | 特点 | 网址 |
|------|------|------|
| **kohya_ss** | 最主流，GUI界面，功能全面 | https://github.com/bmaltais/kohya_ss |
| **sd-scripts** | kohya_ss的核心脚本 | https://github.com/kohya-ss/sd-scripts |
| **LoRA Easy Training Scripts** | 更简单的GUI | https://github.com/Akegarasu/lora-scripts |

**关键训练参数：**

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 学习率 | 1e-4 ~ 5e-5 | 太高过拟合，太低学不够 |
| 网络维度（Dim/Rank） | 16-64 | 越高细节越多但容易过拟合 |
| Alpha | = Dim 或 Dim/2 | 控制学习强度 |
| 训练步数 | 1500-3000 | 视素材量调整 |
| Batch Size | 1-4 | 显存够就大一点 |
| 优化器 | AdamW8bit 或 Prodigy | Prodigy自动调学习率 |

#### 第四步：测试与调优

1. 用训练好的LoRA生成测试图
2. 检查角色一致性（发色、瞳色、面部特征是否正确）
3. 检查是否过拟合（是否只能画一种姿态/表情）
4. 调整参数重新训练直到满意

### 3.3 LoRA的使用

**在Prompt中调用LoRA：**
```
masterpiece, 1girl, <lora:my_character:0.8>, silver hair, blue eyes
```
- `my_character` 是LoRA文件名
- `0.8` 是权重，0.5-1.0常用，太高过拟合，太低没效果

**叠加多个LoRA：**
```
<lora:character_A:0.8>, <lora:style_anime:0.6>, <lora:detail_enhance:0.4>
```

### 3.4 除了LoRA，其他角色一致性方法

| 方法 | 原理 | 适用场景 |
|------|------|----------|
| **IP-Adapter** | 用参考图引导生成 | 快速保持面部一致 |
| **InstantID** | 单张照片保持面部一致 | 最便捷的面部一致性 |
| **Regional Prompter** | 不同区域用不同Prompt | 多角色场景 |
| **CharacterSheet Prompt** | Prompt指定"角色设定图"格式 | 一次生成多角度参考 |

**相关资源：**
- IP-Adapter：https://github.com/tencent-ailab/IP-Adapter
- InstantID：https://github.com/InstantID/InstantID

---

## 第4步：学会I2V视频生成

### 4.1 图生视频（Image-to-Video）基础

**做什么：** 从一张静态图片生成短视频片段（通常2-10秒）。

**这是AI动漫从"图"到"动画"的关键跨越。**

### 4.2 主流I2V工具对比

| 工具 | 特点 | 适合场景 | 网址 |
|------|------|----------|------|
| **Kling（可灵）** | 国产，质量高，5s/10s，动作自然 | 通用首选，国内访问方便 | https://kling.ai |
| **Runway Gen-3** | 海外主流，质量优秀 | 高质量通用视频 | https://runwayml.com |
| **Pika** | 简单易用，有局部重绘 | 快速出片，局部修改 | https://pika.art |
| **AnimateDiff** | SD生态内，开源可控 | 需要精细控制时使用 | https://github.com/guoyww/AnimateDiff |
| **SVD** | SD官方视频模型，开源 | 本地部署，自定义需求 | https://github.com/Stability-AI/generative-models |
| **Wan2.1** | 阿里开源，14B参数 | 本地部署，中文生态 | https://github.com/Wan-Video/Wan2.1 |
| **HunyuanVideo** | 腾讯开源，质量不错 | 本地部署方案 | https://github.com/Tencent/HunyuanVideo |

**I2V关键参数：**
- **运动幅度（Motion Bucket ID）** — 控制画面运动大小
- **FPS** — 帧率，通常6-15fps
- **噪声强度** — 影响生成多样性和稳定性
- **引导帧数** — 参考首帧的强度，越高越忠于原图

### 4.3 动作控制

**精确控制角色动作是最大难点：**

#### 方案一：AnimateDiff + ControlNet（最可控）

- 在ComfyUI中搭建工作流
- 用OpenPose/DWPose指定骨骼动作
- AnimateDiff保证时序连贯
- 可控性最强，但学习曲线陡峭

#### 方案二：Motion Transfer（动作迁移）

- 提供参考视频，AI将动作迁移到目标角色
- 工具：
  - MusePose：https://github.com/TMElyralab/MusePose
  - MagicAnimate：https://github.com/magic-research/magic-animate
- 适合舞蹈、打斗等复杂动作

#### 方案三：Drag-based Animation

- 在画面上拖拽指定运动轨迹
- 工具：DragNUWA：https://github.com/ProjectNUWA/DragNUWA
- 直观但精度有限

#### 方案四：文本描述动作

- 直接用文字描述动作
- 如 "character turns head to the left, hair flowing in wind"
- 最简单但最不可控

### 4.4 口型同步（Lip Sync）

**做什么：** 让角色嘴部动作与配音对齐。

| 工具 | 特点 | 网址 |
|------|------|------|
| **Wav2Lip** | 经典方案，基于音频驱动嘴部 | https://github.com/Rudrabha/Wav2Lip |
| **SadTalker** | 驱动嘴部+头部微动 | https://github.com/OpenTalker/SadTalker |
| **MuseTalk** | 更高质量面部动画 | https://github.com/TMElyralab/MuseTalk |

**流程：**
1. 先生成角色正面视频（嘴部闭合状态）
2. 录制/生成配音
3. 用Lip Sync工具将配音与视频对齐

### 4.5 镜头运动

**方法：**

| 方法 | 说明 |
|------|------|
| I2V工具内置 | Kling、Runway等支持指定镜头运动方向 |
| After Effects | 经典方案，对2D图层添加虚拟摄像机 |
| Deforum | SD插件，支持复杂镜头运动参数化控制 |
| Ken Burns效果 | 最简单，对静态图做缩放+平移 |

**相关资源：**
- Deforum：https://github.com/deforum-art/sd-webui-deforum

---

## 第5步：学会后期合成

### 5.1 配音/音效

#### AI配音工具

| 工具 | 特点 | 网址 |
|------|------|------|
| **GPT-SoVITS** | 开源，少量样本语音克隆 | https://github.com/RVC-Boss/GPT-SoVITS |
| **Bert-VITS2** | 开源，中文效果好 | https://github.com/fishaudio/Bert-VITS2 |
| **ElevenLabs** | 商业服务，质量最高 | https://elevenlabs.io |
| **Fish Speech** | 国产开源，中文优秀 | https://github.com/fishaudio/fish-speech |

#### 音效/BGM

| 工具/资源 | 特点 | 网址 |
|-----------|------|------|
| **Suno** | AI生成风格化音乐 | https://suno.com |
| **Udio** | AI生成高质量音乐 | https://www.udio.com |
| Freesound | 免费音效库 | https://freesound.org |
| Epidemic Sound | 商业音效库 | https://www.epidemicsound.com |

### 5.2 字幕

| 工具 | 特点 | 网址 |
|------|------|------|
| **Whisper** | OpenAI开源语音识别，自动生成字幕 | https://github.com/openai/whisper |
| 剪映 | 国内最方便，自动识别+手动调整 | https://www.capcut.cn |
| Aegisub | 专业字幕编辑器 | https://aegisub.org |

### 5.3 特效

**常用特效类型：**
- 粒子效果 — 樱花飘落、火焰、魔法光效
- 速度线/集中线 — 动漫特有表现手法
- 转场效果 — 淡入淡出、闪白、划变
- 光效叠加 — 镜头光晕、体积光

### 5.4 剪辑拼接

| 工具 | 特点 | 网址 |
|------|------|------|
| 剪映 | 上手最快，AI辅助功能多 | https://www.capcut.cn |
| **DaVinci Resolve** | 专业级，免费版功能足够 | https://www.blackmagicdesign.com/products/davinciresolve |
| Premiere Pro | 行业标准 | https://www.adobe.com/products/premiere |

### 5.5 调色

- **LUT（Look-Up Table）** — 一键应用预设色调
- 动漫常用LUT：Anime LUT、Cinematic LUT
- 手动调色：调整对比度、饱和度、色温
- 风格迁移调色：用AI将参考帧色调迁移到其他帧

---

## 第6步：串联完整工作流

### 6.1 ComfyUI — 工作流中枢

**为什么ComfyUI是核心：**
- 把5个阶段中的大部分AI操作统一在一个平台
- 工作流可以保存、分享、复用
- 社区有大量现成工作流模板
- 支持批处理，提高效率

**ComfyUI核心节点类型：**
- 模型加载 — 加载Checkpoint、LoRA、VAE
- Prompt — 正面/负面提示词
- 采样器 — 控制生成过程
- ControlNet — 姿态/深度/线稿控制
- IP-Adapter — 参考图引导
- AnimateDiff — 视频生成
- 图像后处理 — 放大、修脸、调色

**相关资源：**
- ComfyUI：https://github.com/comfyanonymous/ComfyUI

### 6.2 硬件需求

| 配置 | 能做什么 |
|------|----------|
| RTX 3060 12GB | SD出图 + 简单AnimateDiff，入门最低配 |
| RTX 4070 12GB | SD + AnimateDiff流畅，LoRA训练可行 |
| RTX 4090 24GB | 全流程本地运行，训练速度最快 |
| 云GPU | AutoDL、RunPod等，按小时计费 |

**本地显卡不够时的替代方案：**
- 绘图用云端：Google Colab、AutoDL
- 视频生成用在线服务：Kling、Runway
- LoRA训练用云GPU

### 6.3 完整工作流示例

```
1. 剧本阶段：ChatGPT/Claude生成剧本 → 分镜表 → 每镜头Prompt
2. 角色阶段：SD生成角色立绘 → 训练LoRA → 测试一致性
3. 场景阶段：SD生成各场景背景 → 风格统一 → 场景分层
4. 画面阶段：ComfyUI中 LoRA + ControlNet + IP-Adapter → 逐镜头生成关键帧
5. 动画阶段：关键帧 → AnimateDiff/Kling生成视频片段
6. 口型阶段：配音 → Wav2Lip/SadTalker口型同步
7. 合成阶段：剪映/DaVinci拼接 → 配音/音效 → 字幕 → 调色 → 成片
```

### 6.4 风格差异速览

**日系二次元：**
- Checkpoint：Animagine XL、Counterfeit XL
- 关键词：`anime style, cel shading, vibrant colors`
- 特点：线条清晰、色彩鲜明、大眼睛

**国风/国漫：**
- Checkpoint：国风3 XL、GuoFeng4
- 关键词：`chinese style, ink wash, traditional painting`
- 特点：水墨感、留白、意境

**3D动漫风：**
- Checkpoint：Disney Pixar XL、3D Animation Style
- 关键词：`3d render, pixar style, smooth shading`
- 特点：立体感强、光影丰富

---

## 附录：工具官网与资源汇总

### 核心平台

| 工具 | 说明 | 网址 |
|------|------|------|
| Stable Diffusion | AI图像生成模型 | https://stability.ai |
| ComfyUI | 节点式SD界面 | https://github.com/comfyanonymous/ComfyUI |
| A1111 WebUI | 表单式SD界面 | https://github.com/AUTOMATIC1111/stable-diffusion-webui |
| Civitai | 模型分享社区 | https://civitai.com |
| Hugging Face | 模型托管平台 | https://huggingface.co |

### 图像生成

| 工具 | 说明 | 网址 |
|------|------|------|
| Midjourney | 商业AI绘图 | https://www.midjourney.com |
| NovelAI | 二次元特化AI绘图 | https://novelai.net |
| Flux | 高质量开源模型 | https://bfl.ai |

### 动画/视频生成

| 工具 | 说明 | 网址 |
|------|------|------|
| Kling（可灵） | 国产I2V，质量高 | https://kling.ai |
| Runway | 海外I2V主流 | https://runwayml.com |
| Pika | 简单易用I2V | https://pika.art |
| AnimateDiff | SD生态动画生成 | https://github.com/guoyww/AnimateDiff |
| SVD | SD官方视频模型 | https://github.com/Stability-AI/generative-models |
| Wan2.1 | 阿里开源视频模型 | https://github.com/Wan-Video/Wan2.1 |
| HunyuanVideo | 腾讯开源视频模型 | https://github.com/Tencent/HunyuanVideo |
| Deforum | SD镜头运动插件 | https://github.com/deforum-art/sd-webui-deforum |

### 控制与一致性

| 工具 | 说明 | 网址 |
|------|------|------|
| ControlNet | 结构控制 | https://github.com/lllyasviel/ControlNet |
| IP-Adapter | 参考图引导 | https://github.com/tencent-ailab/IP-Adapter |
| InstantID | 单照面部一致 | https://github.com/InstantID/InstantID |
| DragNUWA | 拖拽式动画控制 | https://github.com/ProjectNUWA/DragNUWA |
| MusePose | 动作迁移 | https://github.com/TMElyralab/MusePose |
| MagicAnimate | 动作迁移 | https://github.com/magic-research/magic-animate |

### LoRA训练

| 工具 | 说明 | 网址 |
|------|------|------|
| kohya_ss | 最主流训练GUI | https://github.com/bmaltais/kohya_ss |
| sd-scripts | 训练核心脚本 | https://github.com/kohya-ss/sd-scripts |
| LoRA Easy Training Scripts | 简化训练GUI | https://github.com/Akegarasu/lora-scripts |
| WD14 Tagger | 自动打标工具 | https://github.com/toriato/stable-diffusion-webui-wd14-tagger |

### 配音/音频

| 工具 | 说明 | 网址 |
|------|------|------|
| GPT-SoVITS | 语音克隆 | https://github.com/RVC-Boss/GPT-SoVITS |
| Bert-VITS2 | 中文TTS | https://github.com/fishaudio/Bert-VITS2 |
| Fish Speech | 国产开源TTS | https://github.com/fishaudio/fish-speech |
| ElevenLabs | 商业高质量TTS | https://elevenlabs.io |
| Suno | AI音乐生成 | https://suno.com |
| Udio | AI音乐生成 | https://www.udio.com |

### 口型同步

| 工具 | 说明 | 网址 |
|------|------|------|
| Wav2Lip | 音频驱动嘴部 | https://github.com/Rudrabha/Wav2Lip |
| SadTalker | 面部+头部动画 | https://github.com/OpenTalker/SadTalker |
| MuseTalk | 高质量面部动画 | https://github.com/TMElyralab/MuseTalk |

### 后期/字幕

| 工具 | 说明 | 网址 |
|------|------|------|
| Whisper | 语音识别生成字幕 | https://github.com/openai/whisper |
| DaVinci Resolve | 专业剪辑调色 | https://www.blackmagicdesign.com/products/davinciresolve |

### 云GPU平台

| 平台 | 说明 | 网址 |
|------|------|------|
| AutoDL | 国内最便宜 | https://www.autodl.com |
| RunPod | 海外按小时计费 | https://runpod.io |
| Google Colab | 免费GPU | https://colab.research.google.com |

### 动漫Checkpoint推荐

| Checkpoint | 风格 | 下载地址 |
|-----------|------|----------|
| Animagine XL | 日系二次元 | https://civitai.com/models/260267/animagine-xl |
| Counterfeit XL | 日系通用 | https://civitai.com/models/118406/counterfeitxl |
| 国风3 XL | 中国风 | Civitai搜索"国风3" |

---

> 本文档基于2025年中的工具生态编写，AI领域发展迅速，建议定期关注Civitai、Hugging Face和各工具GitHub获取最新动态。
