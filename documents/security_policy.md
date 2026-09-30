# Security and Data Handling Policy

## Data Encryption
All customer data is encrypted at rest using AES-256 and in transit using TLS 1.3. Encryption keys are rotated every 90 days and managed through our internal Key Management Service (KMS).

## Access Control
Access to production systems requires multi-factor authentication (MFA). Engineering staff are granted access on a least-privilege basis, reviewed quarterly by the Security team. Any access request outside standard role permissions must be approved by a team lead and logged in the access request system.

## Data Retention
Customer data is retained for the duration of the active subscription plus 90 days after cancellation, after which it is permanently deleted. Backup snapshots are retained for 30 days on a rolling basis.

## Incident Response
In the event of a security incident, the on-call engineer must:
1. Contain the issue within 15 minutes of detection
2. Notify the Security lead and Engineering Director within 30 minutes
3. Begin the incident report within 1 hour
4. Notify affected customers within 72 hours if the incident involves data exposure, per our compliance obligations

## Vendor Access
Third-party vendors with access to production data must sign a Data Processing Agreement (DPA) and undergo an annual security review. Vendor access is automatically revoked if the review is not completed within the renewal window.

## Compliance Certifications
NimbusDesk is SOC 2 Type II certified and GDPR compliant for customers in the EU. HIPAA compliance is available on the Enterprise plan only, as an add-on requiring a signed Business Associate Agreement (BAA).
