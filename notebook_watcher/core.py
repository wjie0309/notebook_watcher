import shutil
import os
import json
from pathlib import Path
import datetime
from loguru import logger
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NotebookArchiver:
    """基于事件触发的自动归档"""
    # 存储默认路径
    CONFIG_DIR = Path(".config")
    CONFIG_DIR.mkdir(exist_ok=True, parents=True)
    DEFAULT_PATH_FILE = CONFIG_DIR / "default_notebook_path.txt"
    
    def __init__(self):
        self.default_path = self._load_default_path()

    def _load_default_path(self):
        """加载默认路径"""
        if self.DEFAULT_PATH_FILE.exists():
            with open(self.DEFAULT_PATH_FILE, 'r', encoding='utf-8') as f:
                return Path(f.read().strip())
        return None

    def _save_default_path(self, path):
        """保存默认路径"""
        with open(self.DEFAULT_PATH_FILE, 'w', encoding='utf-8') as f:
            f.write(str(path))
        self.default_path = path

    def _extract_code_blocks(self, nb_path):
        """自动提取特定标记的代码块"""
        logger.info(f"开始解析文件: {nb_path}")
        with open(nb_path, encoding='utf-8') as f:
            nb = json.load(f)
        
        proto_blocks = [cell for cell in nb['cells'] 
                       if cell['cell_type'] == 'code'
                       and '#proto\n' in cell['source']]
        
        logger.debug(f"发现{len(proto_blocks)}个proto代码块")
        if proto_blocks:
            self._generate_proto_file(nb_path.name, proto_blocks)

    def _generate_proto_file(self, notebook_name, proto_blocks):
        """生成proto源代码文件"""
        proto_dir = Path("src/proto")
        proto_dir.mkdir(exist_ok=True, parents=True)
        
        base_name = notebook_name.replace('.ipynb', '')
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        proto_file = proto_dir / f"{base_name}_{timestamp}_proto.py"
        
        logger.info(f"正在生成proto文件: {proto_file}")
        with open(proto_file, 'w', encoding='utf-8') as f:
            f.write(f"# Generated from {notebook_name}\n")
            f.write(f"# Timestamp: {datetime.datetime.now()}\n\n")
            
            for i, block in enumerate(proto_blocks, 1):
                f.write(f"# Block {i}\n")
                if isinstance(block['source'], list):
                    code = ''.join(block['source'])
                else:
                    code = block['source']
                f.write(code.strip() + "\n\n")
    
    def _get_code_version(self, path):
        """获取指定路径的代码版本"""
        cmd = f'git log -1 --format=%H -- {path}'
        return os.popen(cmd).read().strip()

    def extract_proto_from_folder(self, folder_path=None):
        """从文件夹中提取所有notebook的proto代码
        
        Args:
            folder_path: 要处理的文件夹路径，如果为None则使用默认路径
        """
        if folder_path is None:
            if self.default_path is None:
                logger.error("未指定文件夹路径且没有默认路径")
                return
            folder_path = self.default_path
        else:
            folder_path = Path(folder_path)
            self._save_default_path(folder_path)

        logger.info(f"开始处理文件夹: {folder_path}")
        for nb_file in folder_path.rglob("*.ipynb"):
            logger.info(f"处理文件: {nb_file}")
            self._extract_code_blocks(nb_file)

    def start_daemon(self):
        """启动文件监控守护进程"""
        if self.default_path is None:
            logger.error("未设置默认路径，无法启动守护进程")
            return

        observer = Observer()
        event_handler = NotebookHandler(self)
        observer.schedule(event_handler, path=str(self.default_path), recursive=True)
        observer.start()
        logger.info(f"文件监控已启动，正在监听 {self.default_path} 目录...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

class NotebookHandler(FileSystemEventHandler):
    """自动化文件监控处理器"""
    def __init__(self, archiver):
        self.archiver = archiver
        self.last_processed = time.time()
    
    def on_modified(self, event):
        """文件保存时触发"""
        if not event.is_directory and event.src_path.endswith('.ipynb'):
            if time.time() - self.last_processed > 30:  
                self.last_processed = time.time()
                logger.info(f"检测到文件变更: {event.src_path}")
                self.archiver._extract_code_blocks(Path(event.src_path)) 