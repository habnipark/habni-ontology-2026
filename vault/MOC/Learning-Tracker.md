---
type: "moc"
created: 2026-03-22
updated: 2026-03-22
---

# Learning Tracker

## Not Started

```dataview
TABLE summary, domain, category
FROM "1-Concept" or "2-Project"
WHERE learning-need = true AND learning-status = "not-started"
SORT domain ASC
```

## In Progress

```dataview
TABLE summary, domain, category
FROM "1-Concept" or "2-Project"
WHERE learning-need = true AND learning-status = "in-progress"
SORT updated DESC
```

## Solid (Recent)

```dataview
TABLE summary, domain, category
FROM "1-Concept" or "2-Project"
WHERE learning-status = "solid"
SORT updated DESC
LIMIT 10
```
