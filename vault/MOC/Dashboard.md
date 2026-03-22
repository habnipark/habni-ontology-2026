---
type: "moc"
created: 2026-03-22
updated: 2026-03-22
---

# Dashboard

## Learning Gaps (Not Started)

```dataview
TABLE summary, domain, category
FROM "1-Concept"
WHERE learning-need = true AND learning-status = "not-started"
SORT created DESC
```

## Company Material Digestion

```dataview
TABLE client, period, learning-status
FROM "2-Project"
WHERE source = "company" AND learning-status != "solid"
SORT learning-status ASC
```

## Blog-Ready Material

```dataview
TABLE summary, domain, tags
FROM "1-Concept" or "2-Project"
WHERE visibility = "blog-safe" AND learning-status = "solid"
SORT updated DESC
```

## Books Read This Year

```dataview
TABLE author, rating, read-date
FROM "3-Resource"
WHERE resource-type = "book" AND read-date >= date(2026-01-01)
SORT rating DESC
```

## Recent Notes

```dataview
TABLE type, category, learning-status
SORT created DESC
LIMIT 20
```
