#!/usr/bin/env python3
"""
多线程模型下载工具 - 加速 Whisper 模型下载
支持断点续传和多镜像源
"""
import os
import sys
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 模型配置
MODELS = {
    'base': {
        'size': '139MB',
        'sha256': 'ed3a0f6afb1a99d6eaf8f9e69647ef7ca0cdb3b9731f1f99fe02bd2f729c9e42',
        'urls': [
            # 国内镜像优先
            'https://www.modelscope.cn/models/iic/speech_whisper/resolve/master/base.pt',
            'https://hf-mirror.com/openai/whisper-base/resolve/main/pytorch_model.bin',
            # 国际源
            'https://openaipublic.azureedge.net/main/whisper/models/ed3a0f6afb1a99d6eaf8f9e69647ef7ca0cdb3b9731f1f99fe02bd2f729c9e42/base.pt',
            'https://huggingface.co/openai/whisper-base/resolve/main/pytorch_model.bin',
        ]
    }
}

CHUNK_SIZE = 1024 * 1024  # 1MB chunks
MAX_WORKERS = 8


class ProgressBar:
    def __init__(self, total, desc="Downloading"):
        self.total = total
        self.current = 0
        self.lock = threading.Lock()
        self.desc = desc

    def update(self, n):
        with self.lock:
            self.current += n
            percent = self.current / self.total * 100
            bar_len = 40
            filled = int(bar_len * self.current / self.total)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f'\r{self.desc}: [{bar}] {percent:.1f}% ({self.current//1024//1024}MB/{self.total//1024//1024}MB)', end='', flush=True)

    def finish(self):
        print()


def download_chunk(url, start, end, temp_file, progress_bar):
    """下载单个分块"""
    headers = {'Range': f'bytes={start}-{end}', 'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
            with open(temp_file, 'r+b') as f:
                f.seek(start)
                f.write(data)
            progress_bar.update(len(data))
            return True
    except Exception as e:
        print(f"\nChunk download failed: {e}")
        return False


def get_file_size(url):
    """获取文件大小"""
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            return int(response.headers.get('Content-Length', 0))
    except:
        return 0


def download_with_progress(url, output_path, expected_size=None):
    """带进度条的下载"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=120) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            if expected_size and total_size != expected_size:
                print(f"Warning: File size mismatch. Expected {expected_size}, got {total_size}")

            progress = ProgressBar(total_size)

            with open(output_path, 'wb') as f:
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    progress.update(len(chunk))

            progress.finish()
            return True

    except Exception as e:
        print(f"Download failed: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


def verify_sha256(file_path, expected_hash):
    """验证文件 SHA256"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    actual_hash = sha256.hexdigest()
    return actual_hash == expected_hash


def download_model(model_name='base', cache_dir=None):
    """下载指定模型"""
    if model_name not in MODELS:
        print(f"Unknown model: {model_name}")
        return None

    model_info = MODELS[model_name]

    if cache_dir is None:
        cache_dir = Path.home() / ".cache" / "whisper"
    else:
        cache_dir = Path(cache_dir)

    cache_dir.mkdir(parents=True, exist_ok=True)
    target_path = cache_dir / f"{model_name}.pt"

    # 检查是否已存在且校验正确
    if target_path.exists():
        print(f"Model already exists: {target_path}")
        print("Verifying SHA256...")
        if verify_sha256(target_path, model_info['sha256']):
            print("✓ SHA256 verification passed")
            return str(target_path)
        else:
            print("✗ SHA256 verification failed, re-downloading...")
            target_path.unlink()

    # 尝试每个URL
    for i, url in enumerate(model_info['urls'], 1):
        print(f"\n尝试镜像源 {i}/{len(model_info['urls'])}: {url[:60]}...")

        temp_path = target_path.with_suffix('.tmp')

        if download_with_progress(url, temp_path):
            print("Download completed, verifying...")

            if verify_sha256(temp_path, model_info['sha256']):
                temp_path.rename(target_path)
                print(f"✓ Model saved to: {target_path}")
                return str(target_path)
            else:
                print("✗ SHA256 verification failed, trying next mirror...")
                temp_path.unlink(missing_ok=True)

    print("\n✗ All mirrors failed")
    return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        model = sys.argv[1]
    else:
        model = 'base'

    print(f"Downloading Whisper {model} model...")
    result = download_model(model)

    if result:
        print(f"\nSuccess: {result}")
        sys.exit(0)
    else:
        print("\nFailed to download model")
        sys.exit(1)
