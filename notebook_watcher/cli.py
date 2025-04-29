import argparse
from .core import NotebookArchiver

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description="Notebook Watcher - 监控和提取Jupyter Notebook中的proto代码")
    parser.add_argument("--folder", help="指定要处理的文件夹路径")
    parser.add_argument("--target", help="指定proto代码的存储位置")
    parser.add_argument("--daemon", action='store_true', help="启动监控守护进程")
    
    args = parser.parse_args()
    
    archiver = NotebookArchiver()
    
    # 如果提供了target参数，设置默认proto路径
    if args.target:
        archiver._save_default_proto_path(args.target)
    
    if args.folder:
        archiver.extract_proto_from_folder(args.folder)
    elif args.daemon:
        archiver.start_daemon()
    else:
        # 如果没有指定参数，使用默认路径处理
        archiver.extract_proto_from_folder()

if __name__ == "__main__":
    main() 