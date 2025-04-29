# Notebook Watcher

一个用于监控和提取Jupyter Notebook中proto代码的工具。

## 功能特点

- 自动监控指定目录下的Jupyter Notebook文件
- 提取带有`#proto`标记的代码块
- 支持保存默认监控路径
- 支持递归处理子目录
- 自动生成带时间戳的proto文件

## 安装

```bash
pip install notebook-watcher
```

## 使用方法

### 命令行使用

1. 首次使用时指定监控目录：
```bash
notebook-watcher --folder /path/to/your/notebooks
```

2. 使用默认路径运行：
```bash
notebook-watcher
```

3. 启动守护进程模式：
```bash
notebook-watcher --daemon
```

### Python API使用

```python
from notebook_watcher import NotebookArchiver

# 创建实例
archiver = NotebookArchiver()

# 处理指定目录
archiver.extract_proto_from_folder("/path/to/notebooks")

# 启动守护进程
archiver.start_daemon()
```

## 配置说明

- 默认路径保存在`default_notebook_path.txt`文件中
- 提取的proto代码保存在`src/proto`目录下
- 每个proto文件都会带有时间戳，避免覆盖

## 许可证

MIT License 