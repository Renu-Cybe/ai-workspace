#!/usr/bin/env python3
"""
self-improving script
Continuous improvement through reflection and tracking
Official spec: stdin JSON -> stdout JSON, stderr errors
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

# Force UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def log_error(message: str):
    """Log error to stderr"""
    print(message, file=sys.stderr)


class SelfImproving:
    """Self-improving system with reflection and tracking"""

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.home() / ".claude" / "memory-bank" / "improvement"
        self.records_path = self.base_path / "records"
        self.analysis_path = self.base_path / "analysis"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure directories exist"""
        self.records_path.mkdir(parents=True, exist_ok=True)
        self.analysis_path.mkdir(parents=True, exist_ok=True)

    def record_execution(self, task_type: str, strategy: str, success: bool,
                        duration_sec: float, metadata: Dict = None) -> Dict:
        """Record task execution"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "strategy": strategy,
            "success": success,
            "duration_sec": duration_sec,
            "metadata": metadata or {}
        }

        # Save record
        filename = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        record_file = self.records_path / filename

        try:
            record_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
            return {
                "status": "ok",
                "recorded": True,
                "file": str(record_file)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def analyze_performance(self, task_type: str = None, days: int = 30) -> Dict:
        """Analyze performance for task type or all"""
        cutoff = datetime.now() - timedelta(days=days)
        records = []

        # Load records
        for record_file in self.records_path.glob("*.json"):
            try:
                record = json.loads(record_file.read_text(encoding='utf-8'))
                record_time = datetime.fromisoformat(record["timestamp"])
                if record_time >= cutoff:
                    if task_type is None or record["task_type"] == task_type:
                        records.append(record)
            except Exception as e:
                log_error(f"Error loading {record_file}: {e}")

        if not records:
            return {
                "status": "ok",
                "message": "No records found",
                "records_count": 0
            }

        # Calculate metrics
        total = len(records)
        successful = sum(1 for r in records if r["success"])
        success_rate = (successful / total * 100) if total > 0 else 0

        avg_duration = sum(r["duration_sec"] for r in records) / total if total > 0 else 0

        # Strategy analysis
        strategies = defaultdict(lambda: {"total": 0, "success": 0, "duration": []})
        for r in records:
            s = r["strategy"]
            strategies[s]["total"] += 1
            if r["success"]:
                strategies[s]["success"] += 1
            strategies[s]["duration"].append(r["duration_sec"])

        strategy_scores = {}
        for s, data in strategies.items():
            success = (data["success"] / data["total"] * 100) if data["total"] > 0 else 0
            avg_dur = sum(data["duration"]) / len(data["duration"]) if data["duration"] else 0
            strategy_scores[s] = {
                "total": data["total"],
                "success_rate": round(success, 1),
                "avg_duration_sec": round(avg_dur, 1)
            }

        # Trend (recent vs older)
        mid_point = len(records) // 2
        recent = records[mid_point:]
        older = records[:mid_point]

        recent_success = sum(1 for r in recent if r["success"]) / len(recent) * 100 if recent else 0
        older_success = sum(1 for r in older if r["success"]) / len(older) * 100 if older else 0
        trend = "improving" if recent_success > older_success else "declining" if recent_success < older_success else "stable"

        return {
            "status": "ok",
            "task_type": task_type or "all",
            "records_count": total,
            "success_rate": round(success_rate, 1),
            "avg_duration_sec": round(avg_duration, 1),
            "trend": trend,
            "strategy_analysis": strategy_scores,
            "period_days": days
        }

    def get_recommendation(self, task_type: str) -> Dict:
        """Get strategy recommendation for task type"""
        analysis = self.analyze_performance(task_type, days=30)

        if analysis["records_count"] == 0:
            return {
                "status": "ok",
                "message": "No historical data",
                "recommendation": "try_multiple_strategies",
                "confidence": 0
            }

        strategies = analysis.get("strategy_analysis", {})
        if not strategies:
            return {
                "status": "ok",
                "recommendation": "default",
                "confidence": 0
            }

        # Score strategies
        best_strategy = None
        best_score = 0

        for strategy, data in strategies.items():
            # Weight success rate higher than speed
            score = data["success_rate"] * 0.7 + (100 / (1 + data["avg_duration_sec"])) * 0.3
            if score > best_score:
                best_score = score
                best_strategy = strategy

        confidence = min(analysis["records_count"] / 10, 1.0)  # Max confidence at 10+ records

        return {
            "status": "ok",
            "task_type": task_type,
            "recommendation": best_strategy,
            "confidence": round(confidence, 2),
            "expected_success_rate": strategies[best_strategy]["success_rate"] if best_strategy else 0,
            "alternatives": [s for s in strategies.keys() if s != best_strategy][:3]
        }

    def reflect_on_task(self, task_id: str) -> Dict:
        """Reflect on specific task execution"""
        # Find task by partial ID match
        for record_file in self.records_path.glob("*.json"):
            if task_id in record_file.name:
                try:
                    record = json.loads(record_file.read_text(encoding='utf-8'))

                    reflection = {
                        "status": "ok",
                        "task": record,
                        "insights": []
                    }

                    # Generate insights
                    if record["success"]:
                        reflection["insights"].append("Task completed successfully")
                        if record["duration_sec"] < 60:
                            reflection["insights"].append("Fast execution - efficient approach")
                    else:
                        reflection["insights"].append("Task did not complete successfully")

                    # Compare to average
                    task_type = record["task_type"]
                    analysis = self.analyze_performance(task_type, days=30)
                    avg_duration = analysis.get("avg_duration_sec", 0)

                    if avg_duration > 0:
                        ratio = record["duration_sec"] / avg_duration
                        if ratio < 0.8:
                            reflection["insights"].append(f"Faster than average ({ratio:.1%})")
                        elif ratio > 1.2:
                            reflection["insights"].append(f"Slower than average ({ratio:.1%})")

                    return reflection

                except Exception as e:
                    return {"status": "error", "message": str(e)}

        return {"status": "error", "message": f"Task {task_id} not found"}


def main():
    """Main entry: read from stdin, output to stdout"""
    try:
        if sys.stdin.isatty():
            # Interactive mode - show summary
            si = SelfImproving()
            result = si.analyze_performance()
        else:
            config = json.load(sys.stdin)
            si = SelfImproving()

            action = config.get("action", "record")

            if action == "record":
                result = si.record_execution(
                    config.get("task_type", "unknown"),
                    config.get("strategy", "default"),
                    config.get("success", True),
                    config.get("duration_sec", 0),
                    config.get("metadata", {})
                )
            elif action == "analyze":
                result = si.analyze_performance(
                    config.get("task_type"),
                    config.get("days", 30)
                )
            elif action == "recommend":
                result = si.get_recommendation(
                    config.get("task_type", "unknown")
                )
            elif action == "reflect":
                result = si.reflect_on_task(
                    config.get("task_id", "")
                )
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
