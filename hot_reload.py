"""
热重载模块
监控masu目录下的文件变化，自动重新加载修改的模块
"""
import sys
import importlib
import importlib.util
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from masu.config.logger import terminal


class ModuleReloader:
    """模块热重载器"""
    
    def __init__(self, watch_dir: str = "masu"):
        self.watch_dir = Path(watch_dir)
        self.observer = Observer()
        self._loaded_modules: dict[str, object] = {}
        self._file_to_module: dict[str, str] = {}
        
    def _get_module_name(self, file_path: str) -> str | None:
        """将文件路径转换为模块名"""
        path = Path(file_path)
        if not path.suffix == '.py':
            return None
            
        # 转换为相对路径
        try:
            rel_path = path.relative_to(self.watch_dir.parent)
        except ValueError:
            return None
            
        # 转换为模块路径
        module_parts = list(rel_path.parts)
        if module_parts[-1] == '__init__.py':
            module_parts = module_parts[:-1]
        else:
            module_parts[-1] = module_parts[-1].replace('.py', '')
            
        return '.'.join(module_parts)
    
    def _reload_module(self, module_name: str) -> bool:
        """重新加载指定模块"""
        try:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                importlib.reload(module)
                terminal.info(f"已重载模块: {module_name}", "热重载")
                return True
            else:
                terminal.warning(f"模块未加载，跳过: {module_name}", "热重载")
                return False
        except Exception as e:
            terminal.error(f"重载模块失败 {module_name}: {e}", "热重载")
            return False


class MasuFileHandler(FileSystemEventHandler):
    """Masu文件变化处理器"""
    
    def __init__(self, reloader: ModuleReloader):
        self.reloader = reloader
        self._pending_changes: set[str] = set()
        
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        if not file_path.endswith('.py'):
            return
            
        # 避免重复处理
        if file_path in self._pending_changes:
            return
            
        self._pending_changes.add(file_path)
        
        # 获取模块名并重载
        module_name = self.reloader._get_module_name(file_path)
        if module_name:
            terminal.info(f"检测到文件变化: {file_path}", "热重载")
            self.reloader._reload_module(module_name)
            
        # 清除待处理标记
        self._pending_changes.discard(file_path)
        
    def on_created(self, event):
        """文件创建事件"""
        if not event.is_directory and event.src_path.endswith('.py'):
            terminal.info(f"检测到新文件: {event.src_path}", "热重载")


class HotReloader:
    """热重载管理器"""
    
    def __init__(self, watch_dir: str = "masu"):
        self.watch_dir = Path(watch_dir).absolute()
        self.reloader = ModuleReloader(str(self.watch_dir))
        self.handler = MasuFileHandler(self.reloader)
        self.observer = Observer()
        self._started = False
        
    def start(self):
        """启动文件监控"""
        if self._started:
            terminal.warning("热重载已在运行", "热重载")
            return
            
        try:
            self.observer.schedule(
                self.handler,
                str(self.watch_dir),
                recursive=True
            )
            self.observer.start()
            self._started = True
            terminal.success(f"热重载已启动，监控目录: {self.watch_dir}", "热重载")
        except Exception as e:
            terminal.error(f"启动热重载失败: {e}", "热重载")
            
    def stop(self):
        """停止文件监控"""
        if not self._started:
            return
            
        try:
            self.observer.stop()
            self.observer.join()
            self._started = False
            terminal.info("热重载已停止", "热重载")
        except Exception as e:
            terminal.error(f"停止热重载失败: {e}", "热重载")
            
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


# 全局热重载器实例
hot_reloader = HotReloader(watch_dir="masu")
