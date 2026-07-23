---
name: raci-matrix
description: Generate RACI matrices (Responsible, Accountable, Consulted, Informed) from Odoo user and department data.
  Triggers: "RACI", "responsibility matrix", "who does what",
  "accountability", "RASCI", "roles and responsibilities".
metadata:
  version: 1.0.0
---

# RACI Matrix

Assign roles and responsibilities using RACI framework.

## Data Sources

- `res.users`: people in the organization
- `hr.department`: organizational structure
- `hr.employee`: employee details and managers
- `business.model.canvas`: key activities → tasks to assign

## RACI Definitions

- **R**esponsible — who does the work?
- **A**ccountable — who signs off? (exactly ONE per task)
- **C**onsulted — who provides input? (two-way communication)
- **I**nformed — who needs to know? (one-way communication)

## Process

1. List key activities/tasks from BMC or strategic initiatives
2. List all relevant roles/people from Odoo users
3. For each task, assign R, A, C, I
4. Validate: every task has exactly one A
5. Validate: no person is both R and A on same task (segregation)
6. Flag: tasks with no R, multiple A, or overly consulted

## Anti-patterns to flag
- Too many C's (decision paralysis)
- No A assigned (no accountability)
- Multiple A's (confused authority)
- Same person is R and A (lack of review)
