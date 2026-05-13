# 💡 08_Ideas — Idea Pipeline

> Capture everything. Filter later.
> Use the template: [[05_Life/TEMPLATES/idea]]

## Status Legend
- 💡 Raw — just captured
- 🔬 Researching — investigating feasibility
- 🏗️ Building — promoted to project (→ move to 03_Projects)
- ✅ Launched — live and generating value
- 📦 Archived — decided not to pursue

## Ideas
```dataview
TABLE status as "Status", tags as "Tags"
FROM "08_Ideas"
WHERE file.name != ".gitkeep" AND file.name != "README"
SORT file.mtime DESC
```
