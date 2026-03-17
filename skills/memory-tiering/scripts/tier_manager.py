#!/usr/bin/env python3
"""
memory-tiering script
Four-tier memory management with automatic tier assignment
Official spec: stdin JSON -> stdout JSON, stderr errors
"""

import json
import sys
import io
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Force UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def log_error(message: str):
    """Log error to stderr"""
    print(message, file=sys.stderr)


class MemoryTiering:
    """Four-tier memory management"""

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.home() / ".claude" / "memory-bank"
        self.tiers = {
            "core": self.base_path / "context",
            "working": self.base_path / "active",
            "short_term": self.base_path / "main",
            "long_term": self.base_path / "archive"
        }
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure all tier directories exist"""
        for path in self.tiers.values():
            path.mkdir(parents=True, exist_ok=True)

    def calculate_importance(self, content: str, metadata: Dict) -> float:
        """Calculate importance score (0-100)"""
        score = metadata.get("base_score", 50)

        # Recency factor
        age_days = metadata.get("age_days", 0)
        if age_days <= 1:
            recency = 1.0
        elif age_days <= 7:
            recency = 0.8
        elif age_days <= 30:
            recency = 0.5
        else:
            recency = 0.2

        # Access frequency
        access_count = metadata.get("access_count", 1)
        frequency = min(access_count / 10, 1.0)

        # Content keywords
        critical_keywords = ["preference", "config", "identity", "critical", "important"]
        keyword_boost = 0
        for kw in critical_keywords:
            if kw.lower() in content.lower():
                keyword_boost += 10

        final_score = (score * recency * 0.5) + (frequency * 20) + keyword_boost
        return min(final_score, 100)

    def determine_tier(self, importance: float, age_days: int) -> str:
        """Determine appropriate tier based on importance and age"""
        if importance >= 90:
            return "core"
        elif importance >= 70 or age_days <= 1:
            return "working"
        elif age_days <= 30:
            return "short_term"
        else:
            return "long_term"

    def store(self, content: str, key: str, metadata: Dict = None) -> Dict:
        """Store content in appropriate tier"""
        metadata = metadata or {}
        age_days = metadata.get("age_days", 0)

        importance = self.calculate_importance(content, metadata)
        tier = self.determine_tier(importance, age_days)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{key}_{tier}_{timestamp}.md"

        tier_path = self.tiers[tier]
        file_path = tier_path / filename

        # Prepare content with metadata
        header = f"""---
tier: {tier}
importance: {importance:.1f}
key: {key}
created: {datetime.now().isoformat()}
metadata: {json.dumps(metadata)}
---

"""

        full_content = header + content

        try:
            file_path.write_text(full_content, encoding='utf-8')
            return {
                "status": "ok",
                "tier": tier,
                "importance": importance,
                "path": str(file_path),
                "key": key
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "tier": tier
            }

    def query(self, query_str: str, tiers: List[str] = None) -> Dict:
        """Query across specified tiers"""
        tiers = tiers or ["core", "working", "short_term", "long_term"]
        results = []

        for tier_name in tiers:
            if tier_name not in self.tiers:
                continue

            tier_path = self.tiers[tier_name]
            for file_path in tier_path.glob("*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if query_str.lower() in content.lower():
                        # Extract importance from frontmatter
                        importance_match = re.search(r'importance:\s*([\d.]+)', content)
                        importance = float(importance_match.group(1)) if importance_match else 50

                        results.append({
                            "tier": tier_name,
                            "path": str(file_path),
                            "importance": importance,
                            "snippet": content[:200] + "..." if len(content) > 200 else content
                        })
                except Exception as e:
                    log_error(f"Error reading {file_path}: {e}")

        # Sort by importance
        results.sort(key=lambda x: x["importance"], reverse=True)

        return {
            "status": "ok",
            "query": query_str,
            "tiers_searched": tiers,
            "result_count": len(results),
            "results": results[:10]  # Top 10
        }

    def promote(self, file_path: str, target_tier: str) -> Dict:
        """Promote content to higher tier"""
        src = Path(file_path)
        if not src.exists():
            return {"status": "error", "message": f"File not found: {file_path}"}

        try:
            content = src.read_text(encoding='utf-8')

            # Update tier in content
            content = re.sub(r'tier:\s*\w+', f'tier: {target_tier}', content)

            # Move to new tier
            target_path = self.tiers[target_tier] / src.name
            target_path.write_text(content, encoding='utf-8')

            # Remove original
            src.unlink()

            return {
                "status": "ok",
                "from": src.parent.name,
                "to": target_tier,
                "new_path": str(target_path)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_stats(self) -> Dict:
        """Get memory tier statistics"""
        stats = {}
        total_files = 0

        for tier_name, tier_path in self.tiers.items():
            files = list(tier_path.glob("*.md"))
            total_size = sum(f.stat().st_size for f in files)
            total_files += len(files)

            stats[tier_name] = {
                "file_count": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }

        stats["total_files"] = total_files
        stats["status"] = "ok"
        return stats


def main():
    """Main entry: read from stdin, output to stdout"""
    try:
        if sys.stdin.isatty():
            # Interactive mode - show stats
            mt = MemoryTiering()
            result = mt.get_stats()
        else:
            config = json.load(sys.stdin)
            mt = MemoryTiering()

            action = config.get("action", "store")

            if action == "store":
                result = mt.store(
                    config.get("content", ""),
                    config.get("key", "unnamed"),
                    config.get("metadata", {})
                )
            elif action == "query":
                result = mt.query(
                    config.get("query", ""),
                    config.get("tiers")
                )
            elif action == "promote":
                result = mt.promote(
                    config.get("file_path", ""),
                    config.get("target_tier", "working")
                )
            elif action == "stats":
                result = mt.get_stats()
            else:
                result = {"status": "error", "message": f"Unknown action: {action}"}

        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result.get("status") == "ok" else 1)

    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON: {e}")
        print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
        sys.exit(1)

    except Exception as e:
        log_error(f"Error: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
