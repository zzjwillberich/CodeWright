# CodeWright

**在终端里，把开发任务交给 AI，一起完成代码探索、修改与验证。**

CodeWright 是面向开发者的 AI 编程助手。它以当前项目为工作空间，通过自然语言理解任务，读取和搜索代码、编辑文件、执行命令，并支持把复杂任务拆分给多个 Agent 协作完成。

适合用来熟悉陌生代码库、定位问题、实现功能、补充测试和审查改动。你可以在交互式终端中持续推进任务，也可以通过命令行执行一次性提示。

## 主要特点

| 特点 | 能带来什么 |
| --- | --- |
| 直接在项目里工作 | 将代码搜索、文件修改和命令执行串成开发流程，减少在聊天窗口与编辑器之间搬运上下文。 |
| 灵活接入模型 | 支持 Anthropic、OpenAI 和 OpenAI 兼容服务；配置多个服务后，可在交互界面选择使用。 |
| 可控的执行权限 | 提供操作确认、权限规则、路径检查和危险命令检测，也支持先规划再执行的工作方式。 |
| 多 Agent 协作 | 将探索、实现和验证等任务分配给子 Agent；团队成员可通过消息和共享任务协调工作。 |
| Git Worktree 隔离 | 在独立工作目录与分支中开展任务，方便并行开发与检查改动。 |
| 延续项目上下文 | 支持会话保存与恢复、上下文压缩、项目指令和记忆；交互模式可按检查点回退文件与对话。 |
| 按需扩展 | 通过 Skills 复用工作流程，通过 MCP 接入外部工具，通过 Hooks 在任务事件中触发自定义操作。 |

## 安装与运行

### 1. 准备环境

- Python **3.11 或更高版本**。
- 一个可用的模型 API 服务及对应的 API Key；所选模型需要支持工具调用。
- 使用 Worktree 功能时，需要安装 Git，并在 Git 仓库中启动。

以下命令以 Linux / macOS 的 Bash 或 Zsh 为例。本地电脑和通过 SSH 连接的开发服务器都可以按此方式安装。

### 2. 安装依赖

克隆或下载源码后，在包含 `pyproject.toml` 的项目根目录执行。推荐使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv sync --frozen
source .venv/bin/activate
```

也可以使用 Python 自带的虚拟环境与 pip：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

### 3. 配置模型服务

创建用户级配置目录：

```bash
mkdir -p ~/.codewright
```

在 `~/.codewright/config.yaml` 中填写配置。下面以 Anthropic 接口为例，将 `YOUR_MODEL_ID` 替换为你的服务实际支持的模型 ID：

```yaml
providers:
  - name: claude
    protocol: anthropic
    base_url: https://api.anthropic.com
    model: "YOUR_MODEL_ID"

permission_mode: default
```

通过环境变量提供密钥：

```bash
export ANTHROPIC_API_KEY="你的 API Key"
```

连接其他服务时，按下表调整 `protocol`、`base_url` 和模型 ID：

| 服务类型 | `protocol` | `base_url` | 默认密钥环境变量 |
| --- | --- | --- | --- |
| Anthropic | `anthropic` | `https://api.anthropic.com`，或服务提供方的接口地址 | `ANTHROPIC_API_KEY` |
| OpenAI Responses API | `openai` | `https://api.openai.com/v1`，或支持 Responses API 的接口地址 | `OPENAI_API_KEY` |
| OpenAI Chat Completions 兼容服务 | `openai-compat` | 服务提供方的兼容接口地址 | `OPENAI_API_KEY` |

在 `providers` 列表中添加多个条目，即可配置多个模型服务。非交互运行使用列表中的第一个服务。

也可以在目标项目中创建 `.codewright/config.yaml` 或 `.codewright/config.local.yaml`。程序依次加载用户级配置、项目配置和项目本地配置；后加载配置中的 `providers` 会替换之前的服务列表。

配置文件只保存在本地，密钥通过环境变量提供。本仓库的 `.gitignore` 已排除 `.codewright/`、YAML 配置及 `.env` 文件；在其他项目中使用时，也应将这些本地文件加入该项目的忽略规则。

### 4. 在目标项目中启动

保持安装时的虚拟环境处于激活状态，进入你希望处理的项目目录：

```bash
cd /path/to/your-project
CodeWright
```

然后直接输入任务，例如：

```text
梳理这个项目的入口和主要模块，说明请求是如何流转的。
定位这个测试失败的原因，给出修改方案后再开始改动。
为用户注册接口补充参数校验和测试，并验证修改结果。
```

也可以执行一次性任务：

```bash
CodeWright -p "阅读当前项目，概括目录结构和主要职责"
```

查看启动选项：

```bash
CodeWright --help
```

新开终端时，需要重新激活安装目录下的虚拟环境，并确保 API Key 环境变量已设置。在服务器上使用时，同样先进入目标项目，再从终端启动。

## 常用操作

| 操作 | 说明 |
| --- | --- |
| `/help` | 查看可用命令。 |
| `/plan 任务描述` | 进入规划模式，先分析任务与方案。 |
| `/permission` | 查看权限模式和规则。 |
| `/status` | 查看当前运行状态。 |
| `/compact` | 压缩当前对话上下文。 |
| `/session list` | 查看已保存的会话。 |
| `/session resume` | 列出可恢复的会话。 |
| `/rewind` | 查看可回退的检查点。 |
| `/tasks` | 查看后台任务。 |
| `/worktree list` | 查看已创建的 Worktree。 |

交互界面中，`Enter` 提交输入，`Ctrl+J` 换行，`Esc` 取消当前操作，`Shift+Tab` 切换权限模式。

可以在项目根目录放置 `CODEWRIGHT.md`，说明代码规范、测试方式和项目约定，让助手在后续任务中遵循这些指令。

## 常见启动问题

- **找不到 `CodeWright` 命令**：确认已完成安装，并激活安装目录下的 `.venv`。
- **提示找不到配置文件**：检查 `~/.codewright/config.yaml` 或当前项目的 `.codewright/config.yaml` 是否存在。
- **认证失败或模型不存在**：检查当前终端的 API Key、服务地址和模型 ID；确认所选接口支持对应的协议。
- **无法使用 Worktree**：确认 Git 已安装，当前目录属于已有提交的 Git 仓库。
