"""
视频字幕提取器（四自框架优化版）- 支持 YouTube 和 Bilibili
基于四自原则：自感知 · 自适应 · 自组织 · 自编译

- 自感知：状态追踪、环境检测、决策记录
- 自适应：动态超时、智能重试、资源感知
- 自组织：自动缓存、目录管理、错误归档
- 自编译：并行处理、性能优化、缓存加速

用法: python extract_video.py <视频URL> [--whisper-mode {local|api}]
"""
import sys
import os
from pathlib import Path

# 添加自我纠错系统集成
sys.path.insert(0, str(Path.home() / '.claude' / 'memory-bank' / 'tools'))
try:
    from self_correction_unified import UnifiedSelfCorrection
    _sc = UnifiedSelfCorrection("video-summarizer")
    HAS_SELF_CORRECTION = True
except ImportError:
    HAS_SELF_CORRECTION = False
    _sc = None

import re
import json
import time
import tempfile
import hashlib
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime
from json import JSONDecodeError
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError


# ============ 自感知层：状态追踪与配置 ============

@dataclass
class ExtractionState:
    """自感知：提取状态追踪"""
    url: str
    platform: str = "unknown"
    stage: str = "initialized"
    start_time: float = 0.0
    end_time: float = 0.0
    success: bool = False
    error: Optional[str] = None
    decisions: List[Dict] = None
    metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.decisions is None:
            self.decisions = []
        if self.metrics is None:
            self.metrics = {}
        self.start_time = time.time()

    def record_decision(self, decision: str, reason: str, context: Dict = None):
        """记录关键决策（自感知）"""
        self.decisions.append({
            'timestamp': datetime.now().isoformat(),
            'stage': self.stage,
            'decision': decision,
            'reason': reason,
            'context': context or {}
        })

    def update_stage(self, stage: str):
        """更新当前阶段"""
        self.stage = stage

    def complete(self, success: bool, error: Optional[str] = None):
        """完成状态记录"""
        self.end_time = time.time()
        self.success = success
        self.error = error
        self.metrics['duration'] = self.end_time - self.start_time

    def to_dict(self) -> Dict:
        """导出状态字典"""
        return {
            'url': self.url,
            'platform': self.platform,
            'stage': self.stage,
            'duration': self.metrics.get('duration', 0),
            'success': self.success,
            'error': self.error,
            'decisions': self.decisions,
            'metrics': self.metrics
        }


class SelfAwareness:
    """自感知：环境和状态感知"""

    def __init__(self):
        self.state = None
        self.environment = self._detect_environment()

    def _detect_environment(self) -> Dict[str, Any]:
        """检测运行环境"""
        env = {
            'has_gpu': self._check_gpu(),
            'has_yt_dlp': self._check_yt_dlp(),
            'has_whisper': self._check_whisper(),
            'has_openai': self._check_openai(),
            'network_quality': self._check_network(),
            'cpu_count': os.cpu_count() or 4,
        }
        return env

    def _check_gpu(self) -> bool:
        """检测是否有GPU可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False

    def _check_yt_dlp(self) -> bool:
        try:
            import yt_dlp
            return True
        except:
            return False

    def _check_whisper(self) -> bool:
        try:
            import whisper
            return True
        except:
            return False

    def _check_openai(self) -> bool:
        try:
            import openai
            return True
        except:
            return False

    def _check_network(self) -> str:
        """检测网络质量"""
        test_urls = [
            ('https://www.youtube.com', 'youtube'),
            ('https://www.bilibili.com', 'bilibili')
        ]
        results = {}
        for url, name in test_urls:
            latency = self._measure_latency(url)
            results[name] = latency

        # 返回网络质量评估
        avg_latency = sum(results.values()) / len(results) if results else 5.0
        if avg_latency < 1.0:
            return 'excellent'
        elif avg_latency < 3.0:
            return 'good'
        elif avg_latency < 5.0:
            return 'fair'
        else:
            return 'poor'

    def _measure_latency(self, url: str) -> float:
        """测量到指定URL的延迟"""
        try:
            start = time.time()
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
            urlopen(req, timeout=5)
            return time.time() - start
        except:
            return 10.0

    def create_state(self, url: str) -> ExtractionState:
        """创建新的状态追踪"""
        self.state = ExtractionState(url=url)
        return self.state


# ============ 自适应层：动态策略调整 ============

class SelfAdaptive:
    """自适应：根据环境动态调整策略"""

    # 根据网络质量调整的超时配置
    TIMEOUT_CONFIG = {
        'excellent': {'connect': 5, 'read': 10, 'retry': 1},
        'good': {'connect': 8, 'read': 15, 'retry': 2},
        'fair': {'connect': 12, 'read': 20, 'retry': 3},
        'poor': {'connect': 20, 'read': 30, 'retry': 5}
    }

    def __init__(self, awareness: SelfAwareness):
        self.awareness = awareness
        self.config = self._generate_config()

    def _generate_config(self) -> Dict[str, Any]:
        """根据环境生成自适应配置"""
        network = self.awareness.environment['network_quality']
        has_gpu = self.awareness.environment['has_gpu']

        config = {
            'timeout': self.TIMEOUT_CONFIG.get(network, self.TIMEOUT_CONFIG['fair']),
            'whisper': {
                'model': 'base',  # 可根据GPU调整
                'device': 'cuda' if has_gpu else 'cpu',
                'threads': min(4, os.cpu_count() or 4)
            },
            'download': {
                'max_retries': self.TIMEOUT_CONFIG.get(network, self.TIMEOUT_CONFIG['fair'])['retry'],
                'concurrent': 2 if network in ['excellent', 'good'] else 1
            }
        }
        return config

    def get_timeout(self) -> int:
        """获取当前超时配置"""
        return self.config['timeout']['connect'] + self.config['timeout']['read']

    def get_retry_count(self) -> int:
        """获取重试次数"""
        return self.config['download']['max_retries']

    def should_use_whisper(self, has_subtitle: bool) -> bool:
        """自适应决策：是否使用Whisper"""
        if not has_subtitle:
            return True
        # 如果有字幕但网络质量差，优先使用本地字幕
        if self.awareness.environment['network_quality'] == 'poor':
            return False
        return True


# ============ 自组织层：自动目录和缓存管理 ============

class SelfOrganizing:
    """自组织：自动目录管理和缓存"""

    def __init__(self):
        self.cache_dir = Path.home() / '.claude' / 'cache' / 'video-subtitles'
        self.log_dir = Path.home() / '.claude' / 'memory-bank' / 'errors'
        self._ensure_directories()
        self._cleanup_old_cache()

    def _ensure_directories(self):
        """自动创建必要目录"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _cleanup_old_cache(self, max_age_days: int = 7):
        """自动清理过期缓存"""
        if not self.cache_dir.exists():
            return

        now = time.time()
        max_age = max_age_days * 24 * 3600

        for file in self.cache_dir.iterdir():
            if file.is_file():
                file_age = now - file.stat().st_mtime
                if file_age > max_age:
                    file.unlink()

    def get_cache_key(self, url: str) -> str:
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()

    def get_cached_result(self, url: str) -> Optional[Dict]:
        """获取缓存结果（自组织）"""
        cache_key = self.get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None

    def cache_result(self, url: str, result: Dict):
        """缓存结果（自组织）"""
        cache_key = self.get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to cache result: {e}", file=sys.stderr)

    def log_error(self, error_info: Dict):
        """记录错误（自组织）"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        error_file = self.log_dir / f"extract-error-{timestamp}.json"

        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(error_info, f, ensure_ascii=False, indent=2)
        except:
            pass


# ============ 自编译层：性能优化和并行处理 ============

class SelfCompiling:
    """自编译：性能优化和代码生成"""

    def __init__(self, awareness: SelfAwareness):
        self.awareness = awareness
        self.executor = ThreadPoolExecutor(max_workers=4)

    def parallel_fetch(self, urls: List[str], headers: Dict) -> List[Tuple[str, Optional[Dict]]]:
        """并行获取多个URL（自编译）"""
        results = []

        def fetch_single(url):
            try:
                req = Request(url, headers=headers)
                with urlopen(req, timeout=15) as response:
                    return url, json.loads(response.read().decode('utf-8'))
            except Exception as e:
                return url, {'error': str(e)}

        futures = {self.executor.submit(fetch_single, url): url for url in urls}
        for future in as_completed(futures):
            results.append(future.result())

        return results

    def optimize_segments(self, segments: List[Dict], max_length: int = 100) -> List[Dict]:
        """优化片段：合并短句，去重（自编译）"""
        if not segments:
            return segments

        optimized = []
        current_text = ""
        current_start = segments[0].get('start', 0)

        for seg in segments:
            text = seg.get('text', '').strip()
            if not text:
                continue

            if len(current_text) + len(text) < max_length:
                current_text += " " + text if current_text else text
            else:
                if current_text:
                    optimized.append({
                        'start': current_start,
                        'end': seg.get('start', current_start),
                        'text': current_text
                    })
                current_text = text
                current_start = seg.get('start', 0)

        if current_text:
            optimized.append({
                'start': current_start,
                'end': segments[-1].get('end', current_start),
                'text': current_text
            })

        return optimized

    def generate_summary(self, text: str, max_chars: int = 500) -> str:
        """生成文本摘要（自编译）"""
        if len(text) <= max_chars:
            return text

        # 智能截断：尽量在句子边界截断
        truncated = text[:max_chars]
        last_sentence = truncated.rfind('.')
        if last_sentence > max_chars * 0.7:
            return truncated[:last_sentence + 1]
        return truncated + "..."


# ============ 常量定义 ============
DEFAULT_TIMEOUT = 15
MAX_SEGMENTS = 100

LANG_PRIORITY = [
    'zh', 'zh-CN', 'zh-TW', 'zh-Hans', 'zh-Hant',
    'en', 'en-US', 'en-GB',
    'ja', 'ja-JP'
]

WHISPER_LANG_MAP = {
    'zh': 'zh', 'zh-CN': 'zh', 'zh-TW': 'zh',
    'en': 'en', 'en-US': 'en', 'en-GB': 'en',
    'ja': 'ja', 'ja-JP': 'ja'
}

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

BILIBILI_HEADERS = {
    **DEFAULT_HEADERS,
    'Referer': 'https://www.bilibili.com',
    'Cookie': 'CURRENT_FNVAL=4048'
}

YOUTUBE_PATTERNS = [
    re.compile(r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})'),
    re.compile(r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'),
]

BILIBILI_PATTERNS = [
    re.compile(r'bilibili\.com/video/(BV[a-zA-Z0-9]{10})'),
    re.compile(r'b23\.tv/(BV[a-zA-Z0-9]{10})'),
]


# ============ 核心提取类 ============

class VideoSubtitleExtractor:
    """视频字幕提取器（四自框架）"""

    def __init__(self):
        # 初始化四自层
        self.awareness = SelfAwareness()
        self.adaptive = SelfAdaptive(self.awareness)
        self.organizing = SelfOrganizing()
        self.compiling = SelfCompiling(self.awareness)

    def _sc_wrapper(func):
        """自我纠错装饰器包装"""
        if _sc:
            return _sc.capture_decorator(tool_name="VideoSummarizer", operation=func.__name__)(func)
        return func

    @_sc_wrapper
    def extract(self, url: str, whisper_mode: str = 'local') -> Dict[str, Any]:
        """主提取方法 - 已集成自我纠错"""
        # 自感知：创建状态追踪
        state = self.awareness.create_state(url)

        try:
            # 自组织：检查缓存
            cached = self.organizing.get_cached_result(url)
            if cached:
                state.record_decision('use_cache', 'Found valid cache for URL')
                cached['from_cache'] = True
                cached['extraction_state'] = state.to_dict()
                return cached

            # 自适应：检测平台
            youtube_id = self._extract_id(url, YOUTUBE_PATTERNS)
            bvid = self._extract_id(url, BILIBILI_PATTERNS)

            if youtube_id:
                state.platform = 'YouTube'
                state.update_stage('youtube_extraction')
                result = self._get_youtube_transcript(youtube_id, whisper_mode, state)
            elif bvid:
                state.platform = 'Bilibili'
                state.update_stage('bilibili_extraction')
                result = self._get_bilibili_transcript(bvid, whisper_mode, state)
            else:
                state.complete(False, '无法识别的视频链接')
                return {
                    'error': '无法识别的视频链接',
                    'supported': ['YouTube (youtube.com, youtu.be)', 'Bilibili (bilibili.com, b23.tv)'],
                    'extraction_state': state.to_dict()
                }

            # 自编译：优化结果
            if 'segments' in result:
                result['segments'] = self.compiling.optimize_segments(result['segments'])

            if 'text' in result:
                result['summary'] = self.compiling.generate_summary(result['text'])

            # 自组织：缓存结果
            state.complete(True)
            result['extraction_state'] = state.to_dict()
            self.organizing.cache_result(url, result)

            return result

        except Exception as e:
            error_msg = str(e)
            state.complete(False, error_msg)

            # 自组织：记录错误
            self.organizing.log_error({
                'url': url,
                'error': error_msg,
                'state': state.to_dict(),
                'timestamp': datetime.now().isoformat()
            })

            return {
                'error': error_msg,
                'extraction_state': state.to_dict()
            }

    def _extract_id(self, url: str, patterns: List[re.Pattern]) -> Optional[str]:
        """从URL中提取ID"""
        for pattern in patterns:
            match = pattern.search(url)
            if match:
                return match.group(1)
        return None

    def _http_get_json(self, url: str, headers: Dict[str, str], state: ExtractionState = None) -> Dict[str, Any]:
        """自适应HTTP GET请求"""
        timeout = self.adaptive.get_timeout()
        max_retries = self.adaptive.get_retry_count()

        for attempt in range(max_retries):
            try:
                req = Request(url, headers=headers)
                with urlopen(req, timeout=timeout) as response:
                    content = response.read().decode('utf-8')
                    return json.loads(content)
            except (HTTPError, URLError) as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                return {'error': f'HTTP Error after {max_retries} retries: {str(e)}'}
            except JSONDecodeError as e:
                return {'error': f'JSON Parse Error: {str(e)}'}

        return {'error': 'Max retries exceeded'}

    @_sc_wrapper
    def _get_youtube_transcript(self, video_id: str, whisper_mode: str, state: ExtractionState) -> Dict[str, Any]:
        """获取YouTube字幕（自适应策略）"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)

            # 自感知：记录字幕可用
            state.record_decision('subtitle_available', f'Found {len(list(transcript_list))} subtitle tracks')

            # 自适应：选择最佳字幕
            lang_map = {t.language_code: t for t in transcript_list}
            selected_transcript = self._select_best_subtitle(lang_map, transcript_list, state)

            if selected_transcript:
                data = selected_transcript.fetch()
                full_text = ' '.join(item.text for item in data)

                return {
                    'platform': 'YouTube',
                    'video_id': video_id,
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'language': selected_transcript.language_code,
                    'is_generated': selected_transcript.is_generated,
                    'text': full_text,
                    'segments': [
                        {'start': item.start, 'duration': item.duration, 'text': item.text}
                        for item in data[:MAX_SEGMENTS]
                    ],
                    'source': 'youtube_subtitle'
                }

        except Exception as e:
            error_msg = str(e)
            if 'subtitles are disabled' in error_msg.lower() or 'transcriptsDisabled' in error_msg:
                state.record_decision('no_official_subtitle', 'YouTube subtitles disabled', {'error': error_msg})
            else:
                state.record_decision('subtitle_fetch_failed', error_msg)

        # 自适应：回退到Whisper
        return self._fallback_to_whisper(f'https://www.youtube.com/watch?v={video_id}', whisper_mode, state)

    @_sc_wrapper
    def _get_bilibili_transcript(self, bvid: str, whisper_mode: str, state: ExtractionState) -> Dict[str, Any]:
        """获取Bilibili字幕"""
        try:
            # 获取视频信息
            view_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            data = self._http_get_json(view_url, BILIBILI_HEADERS, state)

            if data.get('code') != 0:
                state.record_decision('video_info_failed', f"API Error: {data.get('message', 'Unknown')}")
                return self._fallback_to_whisper(f'https://www.bilibili.com/video/{bvid}', whisper_mode, state)

            video_info = data['data']
            cid = video_info['cid']
            title = video_info.get('title', 'Unknown')

            # 获取字幕列表
            player_url = f"https://api.bilibili.com/x/player/wbi/v2?cid={cid}&bvid={bvid}"
            player_data = self._http_get_json(player_url, BILIBILI_HEADERS, state)

            subtitle_info = player_data.get('data', {}).get('subtitle', {})
            subtitle_list = subtitle_info.get('subtitles', [])

            if not subtitle_list:
                state.record_decision('no_bilibili_subtitle', 'No CC subtitle available', {'title': title})
                return self._fallback_to_whisper(f'https://www.bilibili.com/video/{bvid}', whisper_mode, state, title)

            # 选择最佳字幕
            sub_map = {sub.get('lan', ''): sub for sub in subtitle_list}
            selected_subtitle = self._select_best_subtitle_bilibili(sub_map, subtitle_list, state)

            if selected_subtitle:
                subtitle_url = urljoin('https:', selected_subtitle['subtitle_url'])
                req = Request(subtitle_url, headers=DEFAULT_HEADERS)

                with urlopen(req, timeout=self.adaptive.get_timeout()) as response:
                    subtitle_content = json.loads(response.read().decode('utf-8'))

                body = subtitle_content.get('body', [])
                full_text = ' '.join(item.get('content', '') for item in body)

                return {
                    'platform': 'Bilibili',
                    'bvid': bvid,
                    'title': title,
                    'url': f'https://www.bilibili.com/video/{bvid}',
                    'language': selected_subtitle.get('lan', 'unknown'),
                    'language_name': selected_subtitle.get('lan_doc', '未知'),
                    'text': full_text,
                    'segments': [
                        {'start': item.get('from'), 'end': item.get('to'), 'text': item.get('content')}
                        for item in body[:MAX_SEGMENTS]
                    ],
                    'source': 'bilibili_subtitle'
                }

        except Exception as e:
            state.record_decision('bilibili_error', str(e))

        return self._fallback_to_whisper(f'https://www.bilibili.com/video/{bvid}', whisper_mode, state)

    def _select_best_subtitle(self, lang_map: Dict, transcript_list, state: ExtractionState):
        """自适应选择最佳字幕"""
        # 优先按语言优先级
        for lang in LANG_PRIORITY:
            if lang in lang_map:
                state.record_decision('subtitle_selected', f'Selected {lang} by priority', {'lang': lang})
                return lang_map[lang]

        # 回退到第一个非生成字幕
        for t in transcript_list:
            if not t.is_generated:
                state.record_decision('subtitle_selected', f'Selected non-generated: {t.language_code}')
                return t

        # 最后回退到第一个
        if transcript_list:
            first = list(transcript_list)[0]
            state.record_decision('subtitle_selected', f'Selected first available: {first.language_code}')
            return first

        return None

    def _select_best_subtitle_bilibili(self, sub_map: Dict, subtitle_list: List, state: ExtractionState):
        """选择Bilibili最佳字幕"""
        for lang in LANG_PRIORITY:
            if lang in sub_map:
                state.record_decision('subtitle_selected', f'Selected {lang} by priority')
                return sub_map[lang]

        if subtitle_list:
            state.record_decision('subtitle_selected', 'Selected first available subtitle')
            return subtitle_list[0]

        return None

    def _fallback_to_whisper(self, url: str, mode: str, state: ExtractionState, title: str = None) -> Dict[str, Any]:
        """自适应回退到Whisper语音识别"""
        state.record_decision('whisper_fallback', 'Falling back to Whisper transcription', {'mode': mode})
        state.update_stage('whisper_transcription')

        # 检查环境
        if mode == 'local' and not self.awareness.environment['has_whisper']:
            return {'error': 'Whisper not installed. Run: pip install openai-whisper'}

        if mode == 'api' and not os.environ.get('OPENAI_API_KEY'):
            return {'error': 'OPENAI_API_KEY not set for Whisper API mode'}

        # 下载并转录
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = os.path.join(temp_dir, 'audio.mp3')

            # 下载音频
            download_result = self._download_audio(url, audio_path, state)
            if isinstance(download_result, dict) and 'error' in download_result:
                return download_result

            # download_result 可能是实际的文件路径（m4a等）
            actual_audio_path = download_result if isinstance(download_result, str) else audio_path

            # 转录
            transcribe_result = self._transcribe_audio(actual_audio_path, mode, state)

            if 'error' in transcribe_result:
                return transcribe_result

            # 合并结果
            transcribe_result.update({
                'url': url,
                'title': title or 'Unknown',
                'platform': 'YouTube' if 'youtube' in url else 'Bilibili',
                'fallback': True,
                'message': '未找到官方字幕，使用Whisper语音识别'
            })

            return transcribe_result

    def _download_audio(self, url: str, output_path: str, state: ExtractionState) -> Union[str, Dict]:
        """自适应下载音频"""
        try:
            import yt_dlp

            # 根据网络质量调整配置
            network = self.awareness.environment['network_quality']
            retries = 3 if network in ['poor', 'fair'] else 2

            # 首先下载原始音频（不转换）
            original_path = output_path.replace('.mp3', '_raw.m4a')
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': original_path,
                'quiet': True,
                'no_warnings': True,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://www.bilibili.com',
                },
                'retries': retries,
                'fragment_retries': retries,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # 查找下载的文件
            base = original_path.replace('_raw.m4a', '')
            actual_path = None
            for ext in ['_raw.m4a', '_raw.mp4', '_raw.webm', '.m4a', '.mp4', '.webm']:
                if os.path.exists(base + ext):
                    actual_path = base + ext
                    break

            if not actual_path:
                return {'error': 'Audio file not found after download'}

            # 使用 ffmpeg 转换为 wav
            wav_path = output_path.replace('.mp3', '.wav')
            try:
                import imageio_ffmpeg
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                cmd = [
                    ffmpeg_exe,
                    '-i', actual_path,
                    '-ar', '16000',  # 16kHz (Whisper要求)
                    '-ac', '1',      # 单声道
                    '-y',            # 覆盖已存在文件
                    wav_path
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                os.remove(actual_path)  # 删除原始文件
                return wav_path
            except Exception as e:
                # 如果转换失败，返回原始文件
                state.record_decision('ffmpeg_conversion_failed', f'FFmpeg conversion failed: {e}', {'fallback': actual_path})
                return actual_path

        except ImportError:
            return {'error': 'yt-dlp not installed. Run: pip install yt-dlp'}
        except Exception as e:
            error_msg = str(e)
            if '412' in error_msg:
                return {'error': 'Bilibili anti-bot protection (HTTP 412). Try using cookies from browser.'}
            return {'error': f'Download failed: {error_msg}'}

    def _transcribe_audio(self, audio_path: str, mode: str, state: ExtractionState) -> Dict[str, Any]:
        """转录音频"""
        if mode == 'api':
            return self._transcribe_with_api(audio_path, state)
        else:
            return self._transcribe_with_local(audio_path, state)

    def _transcribe_with_local(self, audio_path: str, state: ExtractionState) -> Dict[str, Any]:
        """本地Whisper转录（使用transformers格式）"""
        try:
            from transformers import pipeline
            import torch
            import numpy as np
            from pathlib import Path

            # 自适应：根据GPU选择设备
            device = 'cuda' if self.awareness.environment['has_gpu'] else 'cpu'
            state.record_decision('whisper_device', f'Using {device} for transcription')

            # 自感知：记录模型加载
            state.update_stage('whisper_model_load')
            print(f"[自编译] 正在加载 Whisper 模型...", file=sys.stderr)

            # 使用本地transformers模型
            model_path = Path.home() / "whisper-base"
            if not model_path.exists():
                return {'error': '模型未找到。请运行: git clone https://www.modelscope.cn/openai-mirror/whisper-base.git ~/whisper-base'}

            print(f"[自编译] 使用本地模型: {model_path}", file=sys.stderr)

            pipe = pipeline(
                "automatic-speech-recognition",
                model=str(model_path),
                device=0 if device == 'cuda' else -1,
                torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
            )

            # 自感知：记录转录开始
            state.update_stage('whisper_transcribing')
            print(f"[自编译] 模型加载完成，开始转录...", file=sys.stderr)

            # 加载音频（使用torchaudio处理多种格式）
            try:
                import torchaudio
                audio_array, sampling_rate = torchaudio.load(audio_path)
                # 转换为单声道
                if audio_array.shape[0] > 1:
                    audio_array = audio_array.mean(dim=0)
                else:
                    audio_array = audio_array.squeeze(0)
                audio_array = audio_array.numpy()
                # 重采样到16kHz（Whisper要求）
                if sampling_rate != 16000:
                    resampler = torchaudio.transforms.Resample(sampling_rate, 16000)
                    audio_array = resampler(torch.from_numpy(audio_array)).numpy()
                    sampling_rate = 16000
            except ImportError:
                # 回退到librosa
                import librosa
                audio_array, sampling_rate = librosa.load(audio_path, sr=16000, mono=True)

            # 转录音频
            result = pipe(
                {"array": audio_array, "sampling_rate": sampling_rate},
                return_timestamps=True
            )

            # 转换格式
            segments = []
            full_text = result.get('text', '').strip()

            if 'chunks' in result:
                for chunk in result['chunks']:
                    timestamp = chunk.get('timestamp', [0, 0])
                    segments.append({
                        'start': timestamp[0] if timestamp[0] is not None else 0,
                        'end': timestamp[1] if timestamp[1] is not None else timestamp[0] + 5,
                        'text': chunk.get('text', '').strip()
                    })

            return {
                'success': True,
                'text': full_text,
                'segments': segments[:MAX_SEGMENTS],
                'language': result.get('language', 'unknown'),
                'model': 'whisper-base-transformers',
                'source': 'whisper_local'
            }

        except ImportError as e:
            return {'error': f'缺少依赖库。请运行: pip install transformers torch soundfile librosa. 错误: {e}'}
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return {'error': f'Whisper transcription failed: {str(e)}\n{error_detail}'}

    def _transcribe_with_api(self, audio_path: str, state: ExtractionState) -> Dict[str, Any]:
        """Whisper API转录"""
        try:
            import openai

            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return {'error': 'OPENAI_API_KEY not set'}

            client = openai.OpenAI(api_key=api_key)

            with open(audio_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model='whisper-1',
                    file=audio_file
                )

            return {
                'success': True,
                'text': transcript.text,
                'segments': [{'text': transcript.text}],
                'source': 'whisper_api'
            }

        except Exception as e:
            return {'error': f'Whisper API failed: {str(e)}'}


# ============ 命令行入口 ============

def output_json(data: Dict[str, Any], exit_code: int = 0) -> None:
    """统一输出JSON"""
    # Windows 控制台编码处理
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    print(json.dumps(data, ensure_ascii=False, indent=2))
    if exit_code:
        sys.exit(exit_code)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        output_json({
            'error': '请提供视频URL',
            'usage': 'python extract_video.py <URL> [--whisper-mode {local|api}]'
        }, 1)

    url = sys.argv[1].strip()

    if not url.startswith(('http://', 'https://')):
        output_json({'error': '请提供有效的HTTP/HTTPS链接'}, 1)

    # 解析参数
    whisper_mode = 'local'
    if '--whisper-mode' in sys.argv:
        mode_idx = sys.argv.index('--whisper-mode')
        if mode_idx + 1 < len(sys.argv):
            whisper_mode = sys.argv[mode_idx + 1]

    # 创建提取器并执行
    extractor = VideoSubtitleExtractor()
    result = extractor.extract(url, whisper_mode)

    if 'error' in result:
        output_json(result, 1)
    else:
        output_json(result, 0)


if __name__ == '__main__':
    main()
