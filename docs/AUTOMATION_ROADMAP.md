# Automation Roadmap

## North-star outcomes

| Outcome | KPI | 90-day target |
|---|---|---:|
| Scale repeatable delivery | Active governed workflows | 10 |
| Reduce manual effort | Automated workflow stages | >= 75% |
| Protect delivery quality | Quality gate pass rate | >= 98% |
| Improve reliability | SLA attainment | >= 95% |
| Demonstrate value | Validated annualised savings | >= $250k |
| Drive adoption | Monthly active operators | >= 30 |

## Phase 1: Discover and baseline (weeks 1-2)

- Inventory setup, pre-processing, execution, post-processing, and reporting work.
- Score opportunities by volume, manual effort, failure risk, and reuse potential.
- Capture baseline cycle time, quality, cost, rework, and SLA performance.
- Establish workflow ownership, risk tiers, and approval requirements.

Exit criterion: prioritised backlog with measurable baselines and named owners.

## Phase 2: Pilot the service model (weeks 3-6)

- Build three representative workflows through the control-plane contract.
- Integrate API adapters for JIRA, Confluence, and SharePoint behind feature flags.
- Introduce automated quality gates, audit evidence, and rollback procedures.
- Run weekly operator feedback sessions and track adoption friction.

Exit criterion: pilots meet quality targets and demonstrate at least 50% cycle-time reduction.

## Phase 3: Standardise and scale (weeks 7-10)

- Publish reusable workflow templates, runbooks, service levels, and intake criteria.
- Add portfolio dashboards for quality, reliability, adoption, cost, and capacity.
- Establish change control through pull requests, versioning, automated tests, and reviews.
- Train workflow champions and transfer first-line support into delivery teams.

Exit criterion: repeatable onboarding under five working days and >= 75% operator adoption.

## Phase 4: Optimise and govern (weeks 11-13)

- Review low-value steps and exceptions using run-level telemetry.
- Conduct post-implementation reviews and publish validated case studies.
- Allocate capacity using demand, failure, and savings trends.
- Maintain a quarterly automation portfolio review and benefits-realisation audit.

Exit criterion: KPI ownership embedded in BAU governance with a funded improvement backlog.

## Governance gates

1. **Intake:** owner, problem statement, baseline, users, and expected benefit.
2. **Design:** workflow map, controls, data classification, and failure strategy.
3. **Pilot:** test evidence, operator sign-off, monitoring, and rollback.
4. **Scale:** service level, support model, documentation, and training.
5. **Review:** realised benefits, incidents, adoption, lessons, and next actions.
