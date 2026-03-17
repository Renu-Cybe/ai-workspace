"""
性能优化工具模块
提供并行调用、缓存、批量操作等功能
"""

import json
from typing import List, Dict, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
import time


class ParallelReader:
    """并行文件读取器"""

    @staticmethod
    def read_files(file_paths: List[str], max_workers: int = 5) -> Dict[str, Any]:
        """
        并行读取多个文件

        Args:
            file_paths: 文件路径列表
            max_workers: 最大并行数

        Returns:
            Dict[路径, 内容]
        """
        results = {}

        def read_single(path: str) -> tuple:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return path, f.read()
            except Exception as e:
                return path, f"Error: {str(e)}"

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(read_single, path): path for path in file_paths}
            for future in as_completed(futures):
                path, content = future.result()
                results[path] = content

        return results

    @staticmethod
    def read_json_files(file_paths: List[str], max_workers: int = 5) -> Dict[str, Any]:
        """并行读取多个 JSON 文件"""
        results = {}
        text_results = ParallelReader.read_files(file_paths, max_workers)

        for path, content in text_results.items():
            if isinstance(content, str) and not content.startswith("Error:"):
                try:
                    results[path] = json.loads(content)
                except json.JSONDecodeError:
                    results[path] = {"error": "Invalid JSON", "raw": content}
            else:
                results[path] = content

        return results


class FileCache:
    """文件缓存管理器"""

    def __init__(self, maxsize: int = 128):
        self._cache = {}
        self._maxsize = maxsize
        self._access_times = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            self._access_times[key] = time.time()
            return self._cache[key]
        return None

    def set(self, key: str, value: Any):
        """设置缓存"""
        # LRU淘汰
        if len(self._cache) >= self._maxsize:
            oldest = min(self._access_times, key=self._access_times.get)
            del self._cache[oldest]
            del self._access_times[oldest]

        self._cache[key] = value
        self._access_times[key] = time.time()

    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._access_times.clear()

    def get_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "size": len(self._cache),
            "maxsize": self._maxsize,
            "keys": list(self._cache.keys())
        }


# 全局缓存实例
_file_cache = FileCache(maxsize=256)


def cached_read(file_path: str, use_cache: bool = True) -> str:
    """
    带缓存的文件读取

    Args:
        file_path: 文件路径
        use_cache: 是否使用缓存

    Returns:
        文件内容
    """
    if use_cache:
        cached = _file_cache.get(file_path)
        if cached is not None:
            return cached

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if use_cache:
            _file_cache.set(file_path, content)

        return content
    except Exception as e:
        return f"Error: {str(e)}"


def batch_grep(patterns: List[str], paths: List[str]) -> Dict[str, List[str]]:
    """
    批量搜索多个模式

    Args:
        patterns: 搜索模式列表
        paths: 搜索路径列表

    Returns:
        Dict[模式, 匹配结果列表]
    """
    results = {pattern: [] for pattern in patterns}

    def search_in_file(file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in patterns:
                    if pattern in content:
                        results[pattern].append(file_path)
        except:
            pass

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(search_in_file, paths)

    return results


class ResponseOptimizer:
    """响应优化器 - 控制输出质量和长度"""

    @staticmethod
    def summarize_content(content: str, max_length: int = 500) -> str:
        """
        摘要内容

        Args:
            content: 原始内容
            max_length: 最大长度

        Returns:
            摘要后的内容
        """
        if len(content) <= max_length:
            return content

        # 取前30%和后20%，中间用...省略
        head_len = int(max_length * 0.6)
        tail_len = int(max_length * 0.2)

        head = content[:head_len]
        tail = content[-tail_len:] if len(content) > head_len + tail_len else ""

        return f"{head}\n\n... [省略 {len(content) - head_len - tail_len} 字符] ...\n\n{tail}"

    @staticmethod
    def extract_key_points(text: str, num_points: int = 5) -> List[str]:
        """
        提取关键要点

        Args:
            text: 原文
            num_points: 要点数量

        Returns:
            要点列表
        """
        lines = text.split('\n')
        key_points = []

        # 提取标题行、列表项、粗体文本
        for line in lines:
            line = line.strip()
            if line.startswith('#') or line.startswith('- ') or line.startswith('* '):
                key_points.append(line.lstrip('#*- ').strip())
            elif '**' in line:
                # 提取粗体内容
                import re
                bold = re.findall(r'\*\*(.*?)\*\*', line)
                key_points.extend(bold)

            if len(key_points) >= num_points * 2:
                break

        return key_points[:num_points]

    @staticmethod
    def concise_output(result: Any, detail_level: str = "medium") -> str:
        """
        生成简洁输出

        Args:
            result: 原始结果
            detail_level: 详细程度 (low/medium/high)

        Returns:
            简洁输出
        """
        if detail_level == "low":
            return str(result)[:200]
        elif detail_level == "medium":
            if isinstance(result, dict):
                return json.dumps({k: str(v)[:100] for k, v in list(result.items())[:5]}, ensure_ascii=False)
            return str(result)[:500]
        else:
            return str(result)


class ToolCallOptimizer:
    """工具调用优化器"""

    def __init__(self):
        self.call_count = 0
        self.call_log = []

    def should_batch(self, tasks: List[Dict]) -> bool:
        """
        判断是否适合批量执行

        Args:
            tasks: 任务列表

        Returns:
            是否批量
        """
        # 如果任务超过3个且相互独立，建议批量
        return len(tasks) >= 3 and all(t.get('independent', True) for t in tasks)

    def log_call(self, tool: str, duration: float, success: bool):
        """记录工具调用"""
        self.call_count += 1
        self.call_log.append({
            'tool': tool,
            'duration': duration,
            'success': success,
            'timestamp': time.time()
        })

    def get_stats(self) -> Dict:
        """获取调用统计"""
        if not self.call_log:
            return {"total": 0}

        total = len(self.call_log)
        success = sum(1 for log in self.call_log if log['success'])
        avg_duration = sum(log['duration'] for log in self.call_log) / total

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "avg_duration": round(avg_duration, 2)
        }


# 便捷函数

def parallel_read(file_paths: List[str]) -> Dict[str, str]:
    """便捷函数：并行读取多个文件"""
    return ParallelReader.read_files(file_paths)


def parallel_read_json(file_paths: List[str]) -> Dict[str, Any]:
    """便捷函数：并行读取多个 JSON"""
    return ParallelReader.read_json_files(file_paths)


def clear_cache():
    """便捷函数：清空缓存"""
    _file_cache.clear()


def get_cache_stats() -> Dict:
    """便捷函数：获取缓存统计"""
    return _file_cache.get_stats()


# 示例和测试
if __name__ == "__main__":
    print("=== 性能优化工具测试 ===\n")

    # 测试并行读取
    print("1. 测试并行读取...")
    test_files = [
        "~/.claude/memory-bank/context/IDENTITY.md",
        "~/.claude/memory-bank/context/USER.md",
        "~/.claude/memory-bank/context/PROTOCOL.md"
    ]

    # 展开路径
    import os
    test_files = [os.path.expanduser(f) for f in test_files]

    start = time.time()
    results = parallel_read(test_files)
    duration = time.time() - start

    print(f"   读取 {len(results)} 个文件，耗时 {duration:.2f}s")
    for path, content in results.items():
        status = "[OK]" if not content.startswith("Error:") else "[ERR]"
        print(f"   {status} {Path(path).name}: {len(content)} 字符")

    # 测试缓存
    print("\n2. 测试缓存...")
    start = time.time()
    cached = cached_read(test_files[0])
    duration1 = time.time() - start

    start = time.time()
    cached = cached_read(test_files[0])  # 第二次从缓存读
    duration2 = time.time() - start

    print(f"   首次读取: {duration1*1000:.2f}ms")
    print(f"   缓存读取: {duration2*1000:.2f}ms")
    print(f"   加速: {duration1/duration2:.1f}x")

    # 测试响应优化
    print("\n3. 测试响应优化...")
    long_text = "A" * 2000
    summary = ResponseOptimizer.summarize_content(long_text, 500)
    print(f"   原始长度: {len(long_text)}")
    print(f"   摘要长度: {len(summary)}")

    print("\n=== 测试完成 ===")
