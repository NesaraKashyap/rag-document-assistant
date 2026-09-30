# On-Call Engineering Runbook

## Rotation Schedule
The on-call rotation runs weekly, Monday 9am to the following Monday 9am. Rotation assignments are managed in PagerDuty. Engineers are expected to acknowledge pages within 5 minutes during business hours and 15 minutes outside business hours.

## Severity Levels
- **SEV1**: Full outage or data loss risk. Page immediately, all hands. Target resolution: 1 hour.
- **SEV2**: Significant degradation affecting a subset of customers. Page on-call engineer. Target resolution: 4 hours.
- **SEV3**: Minor issue, no customer-facing impact. Log ticket, address in next business day. No page required.

## Common Alerts and First Steps

### Database Connection Pool Exhausted
Check the `db-connections` dashboard in Grafana. If connections are maxed, first check for a recent deploy that may have introduced a connection leak. Restart the affected service pods before escalating.

### Elevated API Error Rate
Check the `api-error-rate` dashboard. Cross-reference with recent deploys in the deploy log. If errors correlate with a deploy, initiate a rollback using `deploy rollback <service-name>`.

### Queue Backlog Growing
Check the `worker-queue-depth` dashboard. Scale up worker pods manually using `kubectl scale deployment workers --replicas=10` if autoscaling hasn't kicked in within 10 minutes.

## Escalation Path
If an issue is not resolved within the SEV1 target window, escalate to the Engineering Director. Contact information is in the internal on-call directory, not included in this document for security reasons.

## Postmortems
All SEV1 and SEV2 incidents require a postmortem document within 3 business days of resolution. Postmortems are blameless and must include a timeline, root cause, and at least 2 concrete follow-up action items with owners assigned.
