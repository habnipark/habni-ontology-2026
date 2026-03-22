---
type: "moc"
created: 2026-03-22
updated: 2026-03-22
---

# Marketing Knowledge Map

## Analytics

```dataview
TABLE summary, learning-status
FROM "1-Concept"
WHERE domain = "web-analytics"
SORT file.name ASC
```

## SEO

```dataview
TABLE summary, learning-status
FROM "1-Concept"
WHERE domain = "seo"
SORT file.name ASC
```

## Ads

```dataview
TABLE summary, learning-status
FROM "1-Concept"
WHERE domain = "ads"
SORT file.name ASC
```

## All Marketing Projects

```dataview
TABLE client, project-status, period
FROM "2-Project"
WHERE contains(tags, "marketing")
SORT period DESC
```
