---
name: memory-tiering
description: |
  Four-tier memory management system inspired by Openviking architecture.
  Manages Core (identity), Working (active context), Short-term (recent history),
  and Long-term (archived) memory layers with automatic promotion and demotion.

tools: [Read, Write, Bash, Glob]
context: fork
---

# Memory Tiering

## Purpose

Implement a four-tier memory management system that automatically organizes information based on importance and recency, optimizing context usage and retrieval efficiency.

## Four Memory Tiers

### 1. Core Memory
- **Content**: Identity, critical configuration, user preferences
- **Persistence**: Permanent
- **Size**: ~100 tokens
- **Location**: `~/.claude/memory-bank/context/`

### 2. Working Memory
- **Content**: Active task context, current session state
- **Persistence**: Session lifetime
- **Size**: ~5k tokens
- **Location**: `~/.claude/memory-bank/active/`

### 3. Short-term Memory
- **Content**: Recent conversations (last 30 days)
- **Persistence**: 30 days
- **Size**: ~50k tokens
- **Location**: `~/.claude/memory-bank/main/`

### 4. Long-term Memory
- **Content**: Archived conversations, historical data
- **Persistence**: Permanent (compressed)
- **Size**: Unlimited
- **Location**: `~/.claude/memory-bank/archive/`

## Usage Scenarios

- **Auto-organize**: Automatically tier information based on importance
- **Query**: Search across all tiers with relevance scoring
- **Promote**: Move important info to higher tiers
- **Archive**: Demote old info to lower tiers
- **Optimize**: Balance context usage across tiers

## Usage

### 1. Store with Tier
```
User: "Store this in Core memory"
User: "Save to Working memory"
User: "Archive to Long-term"
```

### 2. Query Across Tiers
```
User: "Search memory across all tiers"
User: "Find in Core and Working memory"
User: "Query Short-term for recent"
```

### 3. Auto-Tier
```
User: "Auto-tier this information"
User: "Analyze importance and store appropriately"
```

### 4. Optimize
```
User: "Optimize memory tiers"
User: "Balance memory usage"
```

## Workflow

1. **Analyze Content**
   - Score importance (0-100)
   - Determine recency
   - Classify category

2. **Assign Tier**
   - Core: importance > 90
   - Working: importance > 70 or active task
   - Short-term: recent 30 days
   - Long-term: older + archived

3. **Store & Index**
   - Write to appropriate tier
   - Update indices
   - Set metadata

4. **Query & Retrieve**
   - Search across tiers
   - Score relevance
   - Merge results

## Importance Scoring

```
importance = base_score * recency_factor * access_frequency

Where:
- base_score: 0-100 (user defined or auto-detected)
- recency_factor: 1.0 (today) → 0.1 (30 days ago)
- access_frequency: times accessed / total queries
```

## Promotion/Demotion Rules

| From | To | Trigger |
|------|-----|---------|
| Short-term | Working | Accessed > 3 times today |
| Working | Core | Marked as critical |
| Core | Working | Updated, no longer critical |
| Working | Short-term | Task completed, 7 days old |
| Short-term | Long-term | 30 days old |

## Example

**User**: "Store user preference: always use Python 3.11"

**Claude**:
1. Analyzing: High importance (user preference), Permanent relevance
2. Tier assignment: Core Memory
3. Storing: `~/.claude/memory-bank/context/USER.md`
4. Indexed: preference/python/version
