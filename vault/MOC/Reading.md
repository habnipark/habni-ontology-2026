---
type: "moc"
created: 2026-03-22
updated: 2026-03-22
---

# Reading & Resources

## Books

```dataview
TABLE author, rating, read-date, learning-status
FROM "3-Resource"
WHERE resource-type = "book"
SORT read-date DESC
```

## Courses

```dataview
TABLE author, rating, learning-status
FROM "3-Resource"
WHERE resource-type = "course"
SORT read-date DESC
```

## Articles

```dataview
TABLE author, tags
FROM "3-Resource"
WHERE resource-type = "article"
SORT created DESC
LIMIT 20
```
