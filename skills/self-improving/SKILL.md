---
name: self-improving
description: |
  Continuous self-improvement system with execution reflection, performance tracking,
  and strategy optimization. Learns from past executions to improve future performance
  through feedback loops and adaptive behavior adjustment.

tools: [Read, Write, Bash, Glob]
context: fork
---

# Self-Improving

## Purpose

Enable continuous learning and improvement through execution reflection, performance tracking, and adaptive strategy optimization based on historical feedback.

## Core Capabilities

### 1. Execution Reflection
- Analyze completed tasks
- Identify success patterns
- Detect failure modes
- Extract actionable insights

### 2. Performance Tracking
- Record execution metrics
- Track success/failure rates
- Measure time efficiency
- Monitor resource usage

### 3. Strategy Optimization
- Compare approach effectiveness
- Suggest better methods
- Adapt to user preferences
- Learn from feedback

### 4. Feedback Loop
- Collect explicit feedback
- Learn from implicit signals
- Update behavior models
- Apply learned patterns

## Usage Scenarios

- **Post-task Review**: Analyze what worked and what didn't
- **Performance Analysis**: Track improvement over time
- **Strategy Selection**: Choose best approach based on history
- **Preference Learning**: Adapt to user working style

## Usage

### 1. Record Execution
```
User: "Record this task execution"
User: "Log success with strategy A"
User: "Track performance of this approach"
```

### 2. Reflect on Task
```
User: "Analyze last execution"
User: "What worked well?"
User: "Review task performance"
```

### 3. Get Recommendations
```
User: "Suggest best strategy for this task"
User: "Based on history, what approach?"
User: "Recommend based on past success"
```

### 4. View Performance
```
User: "Show performance stats"
User: "Track my progress"
User: "How am I improving?"
```

## Workflow

1. **Start Task**
   - Record task metadata
   - Initialize tracking
   - Set baseline metrics

2. **Execute & Monitor**
   - Log key actions
   - Track time/resource usage
   - Record intermediate results

3. **Complete & Reflect**
   - Mark completion status
   - Analyze execution path
   - Identify patterns

4. **Learn & Adapt**
   - Update performance models
   - Adjust strategy weights
   - Apply to future tasks

## Performance Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| Success Rate | % of successful completions | 0-100% |
| Time Efficiency | Actual vs estimated time | 0-200% |
| Quality Score | User feedback rating | 0-5 stars |
| Strategy Effectiveness | Approach success rate | 0-100% |

## Learning Model

```
strategy_score = historical_success * 0.5 +
                 recent_success * 0.3 +
                 user_feedback * 0.2

recommendation = argmax(strategy_scores)
```

## Feedback Types

1. **Explicit**: User directly rates/feedback
2. **Implicit**: Derived from behavior (retries, time spent)
3. **Comparative**: A/B test different approaches
4. **Temporal**: Performance trends over time

## Example

**User**: "Analyze my Python coding tasks"

**Claude**:
1. Reflection:
   - 15 tasks analyzed
   - 87% success rate
   - Common pattern: Fast success with type hints

2. Insights:
   - Strategy "write tests first" has 95% success
   - Average time decreased 20% over last 10 tasks
   - User prefers docstrings for public functions

3. Recommendations:
   - Continue using type hints
   - Add tests before implementation
   - Include docstrings for API functions

4. Applied:
   - Updated default approach for Python tasks
