# HEARTBEAT.md - 心跳维护配置

> **心跳配置文件** - 定义定期维护任务和检查项
> 此文件在上下文压缩后必须保留

---

## 心跳周期

| 频率 | 任务 | 最后执行 |
|------|------|----------|
| 每次启动 | 加载上下文、检查当前会话 | - |
| 会话结束 | 保存会话、更新索引 | - |
| 每日 22:00 | 记忆清理、生成日报 | - |
| 每周日 20:00 | 生成周报告、归档旧数据 | - |

## 启动检查清单

```
□ 加载 IDENTITY.md
□ 加载 USER.md
□ 加载 PROTOCOL.md
□ 检查 session/current.md（异常恢复）
□ 检测当前 git 分支
□ 加载对应分支记忆
□ 执行清理检查
```

## 会话结束检查

```
□ 保存当前会话到 sessions/YYYY-MM-DD.md
□ 更新 errors/index.json
□ 生成会话摘要
□ 清理临时文件
□ 删除 session/current.md
```

## 每日任务 (22:00)

### 记忆清理
- [ ] 归档超过30天的 sessions/
- [ ] 压缩 errors/ 旧记录
- [ ] 更新 stats/weekly-report

### 技能维护
- [ ] 扫描 skills/ 更新知识库
- [ ] 提取新知识点
- [ ] 检查技能关联性

### 错误分析
- [ ] 统计当日错误
- [ ] 识别高频问题
- [ ] 更新预防措施

## 每周任务 (周日 20:00)

### 周报告生成
- [ ] 生成 errors/stats/weekly-report-YYYY-MM-DD.md
- [ ] 分析错误趋势
- [ ] 生成改进建议

### 归档整理
- [ ] 归档已完成 todos/
- [ ] 压缩旧 sessions/
- [ ] 更新 decisions/ 索引

## 手动触发命令

```bash
# 检查记忆库状态
bash ~/.claude/memory-bank/tools/check-status.sh

# 手动清理
python ~/.claude/memory-bank/tools/memory_cleanup.py

# 生成周报告
python ~/.claude/memory-bank/tools/self_correction.py -c "from self_correction import generate_weekly_report; generate_weekly_report()"

# 切换分支记忆
bash ~/.claude/memory-bank/tools/switch-branch.sh <branch-name>
```

## 紧急维护

### 上下文压缩后
如果触发了上下文压缩，立即执行:
```
1. 重新加载 context/IDENTITY.md
2. 重新加载 context/USER.md
3. 重新加载 context/PROTOCOL.md
4. 重新加载 context/HEARTBEAT.md
```

### 记忆库损坏
如果发现记忆库异常:
1. 检查备份: `~/.claude/memory-bank/backups/`
2. 恢复最近备份
3. 重新索引: `python tools/rebuild-index.py`

---
*最后更新: 2026-03-17 | 架构版本: v2.0*
