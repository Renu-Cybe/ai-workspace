# four-self-framework Reference

## 内部实现细节

### 四自原则

1. **自感知 (Self-awareness)**: 识别自身状态和环境
2. **自适应 (Self-adaptation)**: 根据反馈调整行为
3. **自组织 (Self-organization)**: 自动管理和优化结构
4. **自编译 (Self-compilation)**: 自我改进和升级

### 输出格式

```json
{
  "status": "ok|error",
  "message": "result message",
  "data": {
    "awareness": {},
    "adaptation": {},
    "organization": {},
    "compilation": {}
  }
}
```

### 错误处理

- 核心框架错误：记录到 memory-bank/errors/
- 状态异常：自动触发自适应机制
- 执行失败：降级到安全模式

## 开发 notes

- 创建时间: 2026-03-17
- 遵循官方三层架构
- 纯框架型 Skill，无 scripts 目录
