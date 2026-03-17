---
name: memory-searching
description: |
  Advanced memory search with semantic understanding and context awareness.
  Supports keyword, tag, temporal, and similarity-based search across memory tiers.
  Optimizes search strategies based on historical success rates.

tools: [Read, Glob, Grep, Bash]
context: fork
---

# Memory Searching

## Purpose

Enhanced memory search capabilities combining keyword, semantic, and contextual search methods for efficient information retrieval.

## Usage Scenarios

- Search through archived conversations
- Find related memories by context
- Semantic search using meaning not just keywords
- Filter by tags, time range, or project

## Usage

### 1. Keyword Search
```
User: "Search for 'performance optimization' in memory"
User: "Find conversations about Python skills"
```

### 2. Semantic Search
```
User: "Search similar to 'memory management'"
User: "Find related to error handling"
```

### 3. Filtered Search
```
User: "Search for 'dashboard' in last 30 days"
User: "Find with tag 'important'"
```

### 4. Combined Search
```
User: "Search 'optimization' with high importance"
User: "Find similar to current task"
```

## Workflow

1. **Parse Query**
   - Extract keywords
   - Identify filters (time, tags, importance)
   - Detect search type

2. **Execute Search**
   - Keyword: grep-based search
   - Semantic: vector similarity
   - Temporal: time-range filter
   - Combined: multi-criteria scoring

3. **Rank Results**
   - Relevance scoring
   - Historical success weighting
   - Recency bonus

4. **Present Results**
   - Top N results
   - Context snippets
   - Navigation links

## Search Types

| Type | Method | Use Case |
|------|--------|----------|
| Keyword | Grep | Exact match |
| Semantic | TF-IDF | Concept similarity |
| Temporal | Date filter | Time-based |
| Tag | Metadata | Category search |
| Combined | Multi-score | Complex queries |

## Scoring Formula

```
score = relevance * 0.5 + success_rate * 0.3 + recency * 0.2
```

## Example

**User**: "Search for 'skill generator'"

**Claude**: Searching memory...
- Found 5 relevant conversations
- Top result: "skill_generator.py development" (2026-03-17)
- Related tags: #skills, #code-generation
