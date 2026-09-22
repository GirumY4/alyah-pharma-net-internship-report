## Summary of the Project

The project work of this internship is the design, implementation, and
production deployment of **Alyah Pharma Net**, a multi-tenant SaaS platform
for pharmaceutical logistics in Ethiopia. The platform was built within
Alyah Software — the enterprise software division of the Alyah Technologies
group, the company hosting this internship — as an in-house product
initiative that consolidates several of the group's service lines into one
deliverable system.

Alyah Pharma Net serves two audiences simultaneously. For **independent
pharmacies**, it is a SaaS management dashboard in which each pharmacy
operates as an isolated tenant of a shared backend: managing its own
medicine catalogue, tracking batches with expiry and GTIN traceability,
receiving and fulfilling consumer orders, recording payments, generating
regulatory-grade reports, and maintaining an immutable audit trail of every
data-modifying action. For **patients and public consumers**, it is a
centralized digital marketplace in which a single search reveals live
medicine availability across all onboarded pharmacies — replacing the
current "phone call and walk-in" model — while exposing none of the
sensitive operational fields that pharmacies use internally. A system
administrator console provides cross-tenant governance, platform-wide
analytics, and access to the full audit trail for oversight and compliance
review.

Technically, the platform is a MERN-stack system (MongoDB, Express v5,
React 19, Node.js) written end-to-end in TypeScript, deployed on three
cloud platforms: the shared backend on Render, the SaaS dashboard on Vercel,
and the database on MongoDB Atlas. It implements multi-tenant data isolation
through `pharmacyId` keys extracted from signed JWTs, atomic stock deduction
inside database sessions, schema-level immutability on audit and ledger
collections (simulating ALCOA+ and 21 CFR Part 11 data integrity), FEFO
batch selection on order approval (aligning with the EFDA Traceability
Directive), and a public marketplace aggregation pipeline that joins
medicine records with their owning pharmacy while withholding operational
fields. The work was executed against four governing documents — an IEEE
29148-aligned SRS, an SDS, an API contract, and a database schema reference
— treated as the single source of truth throughout implementation.

## Problem Statement and Justification

The problem this project addresses is the absence of a digital, auditable,
multi-tenant infrastructure for pharmaceutical logistics among independent
pharmacies in Ethiopia. Three interrelated gaps define the current state.

**First, medicine discovery is fragmented and inefficient.** Patients and
public consumers today locate a required medicine by visiting or telephoning
pharmacies one by one. A patient searching for a specific brand, dosage, or
generic equivalent may spend hours without knowing whether any pharmacy in
their city actually stocks the item. This friction is particularly acute for
chronic-disease patients, rare medicines, and after-hours emergencies, and
it represents a direct access-to-care failure that a centralized digital
marketplace can resolve.

**Second, independent pharmacies manage stock with paper or spreadsheets.**
Without a shared digital catalogue, batch-level expiry tracking, or a
formal reorder-alert mechanism, pharmacies frequently miss reorder windows,
accumulate near-expiry stock that is dispensed last rather than first, and
lack the real-time stock visibility required to promise availability to
customers. The commercial consequence is lost sales; the public-health
consequence is expired medicine reaching patients.

**Third, there is no audit trail for commercial and clinical actions.**
Under the Ethiopian Food and Drug Authority (EFDA) Traceability Directive,
pharmaceutical distributors are expected to demonstrate traceability at the
batch and unit level — including GS1 Global Trade Item Number (GTIN)
recording, First-Expiring-First-Out (FEFO) dispensing discipline, and
attributable records of every stock mutation. Most independent pharmacies
today have no mechanism to produce such records; a platform that enforces
immutability, attribution, and contemporaneous timestamping at the software
level would allow them to satisfy these requirements without building
compliance tooling individually.

These three gaps share one structural root: each pharmacy currently
operates as a closed, non-interoperable unit. A multi-tenant SaaS platform
— in which a shared backend isolates each pharmacy's operational data while
exposing a cross-tenant public search surface — is the minimal architecture
that can close all three gaps at once, and it is the architecture this
project delivers.

## Objectives of the Project

### General Objective

To design, implement, and deploy a production multi-tenant SaaS
pharmaceutical logistics platform that enables independent Ethiopian
pharmacies to manage inventory, fulfill orders, and demonstrate regulatory-
grade traceability, while simultaneously giving public consumers a unified
marketplace to discover medicine availability across all onboarded
pharmacies.

### Specific Objectives

- **SO-1.** Design a shared-database multi-tenant architecture in which
  every tenant-scoped query and mutation is automatically filtered by the
  authenticated pharmacy's `pharmacyId`, provably preventing cross-tenant
  data leakage.
- **SO-2.** Implement a complete medicine catalogue module with batch-level
  tracking (batch number, GTIN, expiry date, manufacture date, supplier,
  shelf location) and a reorder-threshold alert mechanism, satisfying
  FR-2.1 through FR-2.6 of the SRS.
- **SO-3.** Implement an immutable GRN/GIN stock ledger in which every
  stock mutation is recorded as a non-updateable, non-deletable transaction
  entry, satisfying FR-2.7 and NFR-4.4.
- **SO-4.** Implement a cross-tenant consumer order lifecycle in which a
  public user places an order against a specific pharmacy, the pharmacy
  manager approves it, and stock is atomically deducted with FEFO batch
  selection inside a database transaction, satisfying FR-3.1 through FR-3.5.
- **SO-5.** Implement a payment recording module that aggregates completed
  payments against an order and atomically updates the order's payment
  status (unpaid, partially paid, paid) while preventing overpayment,
  satisfying FR-4.1 through FR-4.4.
- **SO-6.** Implement tenant-scoped and platform-wide reporting endpoints
  for inventory valuation, sales statistics, expiry forecasting, and cross-
  tenant platform metrics, satisfying FR-5.1 through FR-5.5.
- **SO-7.** Implement an append-only audit log that records the actor,
  action type, resource, before/after state, IP address, and User-Agent for
  every data-modifying operation, satisfying NFR-4.1 and ALCOA+ data-
  integrity principles.
- **SO-8.** Deploy the platform to production on three cloud services
  (Render, Vercel, MongoDB Atlas) with environment separation, secrets
  management, and a post-deployment verification checklist.

## Methodology

The project followed a **specification-driven, iteratively phased
methodology** adapted from IEEE 29148 (Systems and software engineering —
Life cycle processes — Requirements engineering). Rather than treating
specifications as an up-front gate and then switching to implementation,
the four governing documents — the SRS, the SDS, the API documentation,
and the database schema reference — were maintained as living artifacts
throughout the project and were the authoritative reference for every
implementation decision, code review, and test.

### Requirement Engineering

The Software Requirements Specification was drafted first and organized
into five feature domains (Authentication & Access Control, Inventory &
Medicines, Orders & Fulfillment, Payments, Reports & Analytics), each
requirement assigned a stable identifier (e.g., FR-2.3, NFR-4.1) and
mapped to a test case ID in a requirement traceability matrix. This made
every requirement testable by design: an implementation either satisfied
its acceptance criteria or it did not, and no requirement was considered
done until its mapped test case had been exercised manually.

### Design Specification

The Software Design Specification translated the SRS into implementation
contracts. It defined the entity-relationship model across six MongoDB
collections, the schema-level constraints and indexes for each collection,
the middleware pipeline (authentication → tenant gate → RBAC → controller),
the atomicity guarantees for stock mutation, and the immutability
enforcement mechanism for the audit and ledger collections. The SDS also
specified the feature-based folder structure of both the backend and the
frontend, which the implementation then followed exactly.

### API Contract and Database Schema Reference

A REST API documentation document defined every endpoint, its HTTP method,
its access roles, its request and response shape, its error codes, and its
mapping to SRS requirements. A companion database schema reference
documented every collection, field, index, and virtual property. Together
these two documents allowed the frontend and mobile teams to build against
stable contracts while the backend was still being implemented.

### Iterative Phased Implementation

Implementation proceeded in four two-week phases aligned with the SDS:

<!-- table: Phased implementation plan aligned with the Software Design Specification -->
| Phase | Focus | Key Deliverables |
| --- | --- | --- |
| Phase 1 | Foundation | Repository scaffolding, MongoDB connection, centralized error handler, JWT authentication, RBAC middleware, user management module. |
| Phase 2 | Compliance primitives | Audit logger utility, immutable audit log schema, centralized error mapper for the frontend. |
| Phase 3 | Inventory & stock logic | Tenant-scoped medicine CRUD, batch and expiry tracking, immutable inventory transaction model, GRN/GIN endpoints, low-stock virtual property, global marketplace search API. |
| Phase 4 | Orders, payments & UI | Cross-tenant order placement, fulfillment status workflow, atomic stock deduction, payment recording, SaaS dashboard, tenant-scoped and platform-wide reports. |

Each phase ended with a working, deployed increment rather than a
document, so the platform was runnable throughout development and could be
demonstrated to the company supervisor at each milestone.

### Version Control and Collaboration

The team worked in a shared Git repository with a protected `main` branch
and short-lived feature branches. Commits followed the Conventional Commits
format. No change was merged to `main` without peer review, and several
modules underwent structured **comparative reviews** in which parallel
implementations of the same module were compared against the specification
and consolidated into a single production-grade version.

### Testing and Verification

Verification was performed through:

- **Manual API exercise** using Postman and curl for every endpoint against
  the requirement traceability matrix;
- **Browser-based functional testing** of the SaaS dashboard across all
  three role perspectives (public user, pharmacy manager, administrator);
- **Tenant isolation tests** in which a pharmacy manager's JWT was used to
  attempt cross-tenant access and verified to fail on every scoped endpoint;
- **Concurrency tests** on the atomic stock deduction path to verify no
  negative stock could be produced under simulated simultaneous approvals;
- **Deployment verification** via a post-deployment checklist executed
  against the live production environment on Render, Vercel, and Atlas.

The most important process limitation — the absence of an automated unit
and integration test suite — is acknowledged as the principal weakness of
the methodology and is addressed in the recommendations of this part.

## Analysis, Results and Discussion

### Implemented Modules and Requirement Coverage

The delivered platform implements the complete surface defined in the SRS.
The mapping between the seven specific objectives and the implemented
artefacts is summarized below.

<!-- table: Traceability of specific objectives to implemented modules -->
| Objective | Module | Key Source Files |
| --- | --- | --- |
| SO-1: Multi-tenant isolation | Authentication + RBAC middleware | auth.middleware.ts, rbac.middleware.ts |
| SO-2: Medicine catalogue | Inventory module | medicine.model.ts, medicine.controller.ts |
| SO-3: Immutable GRN/GIN ledger | Inventory transactions module | inventoryTransaction.model.ts, inventory.service.ts |
| SO-4: Order lifecycle | Orders module | orders.model.ts, orders.service.ts, orders.controller.ts |
| SO-5: Payment recording | Payments module | payments.model.ts, payments.service.ts, payments.controller.ts |
| SO-6: Reports | Reports module | reports.service.ts, reports.controller.ts |
| SO-7: Audit trail | Audit logger utility | auditLogger.ts, auditLogs.model.ts, auditLogs.controller.ts |
| SO-8: Production deployment | Operations | Render, Vercel, MongoDB Atlas |

Every functional requirement in the SRS (FR-1.1 through FR-5.5) has a
corresponding implemented endpoint or UI surface; every non-functional
requirement listed in the traceability matrix (NFR-1.4 through NFR-4.4)
has a corresponding implementation mechanism.

### Deployment Results

The platform was deployed to production across three services:

<!-- table: Production deployment configuration and verification status -->
| Component | Provider | Production Address | Verification |
| --- | --- | --- | --- |
| Shared backend API | Render | https://alyah-pharma-net-platform.onrender.com | GET /health returns 200 OK |
| SaaS web dashboard | Vercel | https://alyah-pharma-net.vercel.app | Login, dashboard, marketplace load without console errors |
| Database | MongoDB Atlas | SRV connection string in Render secrets | Connections visible in Atlas metrics |

The deployment process exposed and resolved seven platform-specific issues
(documented in Appendix D of this report): the Render build service
omitting TypeScript type packages, case-sensitivity of the Linux
filesystem rejecting mismatched import casing, a missing database
connection variable crashing the server at boot, an un-whitelisted
frontend origin producing CORS rejections, a missing build-time API base
URL producing a blank frontend, and two related runtime defects in the
frontend pagination handling and component exports. Each was resolved with
a specific engineering measure that is now a permanent part of the
deployment pipeline.

### Tenant Isolation Verification

The single most important correctness property of a multi-tenant platform
is that one tenant cannot read or mutate another tenant's data. This
property was verified through three complementary mechanisms:

1. **Code-level enforcement.** Every tenant-scoped query is filtered by a
   `pharmacyId` derived exclusively from the verified JWT payload by a
   dedicated middleware. Client-supplied `pharmacyId` values in the request
   body or query string are ignored for non-admin roles.
2. **Manual cross-tenant testing.** A pharmacy manager's JWT was used to
   issue requests for orders, medicines, payments, reports, and audit logs
   with a different pharmacy's identifier substituted in the request;
   every such request returned either an empty result or a 404, never
   cross-tenant data.
3. **Audit log inspection.** The audit log endpoint, when queried by a
   pharmacy manager, returned only entries whose `pharmacyId` matched the
   manager's tenant — verifying that even the observability surface is
   scoped.

No cross-tenant access path was found during testing.

### Data-Integrity Verification

Two collections — `auditLogs` and `inventoryTransactions` — are declared
immutable at the schema level through Mongoose pre-hooks that reject every
`updateOne`, `updateMany`, `replaceOne`, `findOneAndUpdate`,
`findOneAndReplace`, `deleteOne`, `deleteMany`, and `bulkWrite` operation.
During testing, attempts to mutate existing documents in either collection
were rejected at the database layer, confirming that immutability is
enforced by construction rather than by convention.

The GRN/GIN ledger also correctly records every stock mutation with
`stockBefore`, `stockAfter`, `quantityChanged`, `batchNumber`, `actor`,
and timestamp, producing a complete, attributable, contemporaneous, and
original record of stock history — the four properties required by ALCOA+.

### Discussion

The project demonstrates that a single team, working within a six-week
internship window and using a specification-driven methodology, can deliver
a production multi-tenant SaaS platform with regulatory-grade data-
integrity properties. The most consequential design decisions were, in
retrospect, three:

- **Treating specifications as living documents.** Because the SRS, SDS,
  API contract, and schema reference were maintained throughout the
  project, drift between intention and implementation was caught in code
  review rather than in testing.
- **Enforcing immutability at the schema layer.** Delegating data
  integrity to Mongoose pre-hooks rather than to application-layer checks
  meant that even a buggy or malicious controller could not mutate an
  audit or ledger record.
- **Using atomic database operations for stock mutation.** The `$inc`
  operator inside a transactional session, guarded by a sufficient-stock
  condition, eliminated an entire class of race-condition bugs that would
  otherwise have surfaced only under production concurrency.

The principal limitations are discussed in the conclusion of this part and
inform the recommended future work.

## Proposed Solution: The Implemented System

### High-Level Architecture

The implemented platform follows a three-tier multi-tenant architecture,
illustrated in the figure below.

![High-level multi-tenant architecture of Alyah Pharma Net](assets/images/architecture.png)

At the **client tier**, three applications consume the shared backend:

- The **React SaaS Dashboard**, built with React 19, Vite, TypeScript, and
  MUI, is the primary workspace for Pharmacy Managers and System
  Administrators. It hosts the tenant dashboard, inventory grid, order
  fulfillment workspace, payment drawer, reports and analytics pages,
  profile settings, and administrator user-management console.
- The **Mobile Consumer App**, built by the dedicated mobile team, is the
  public-facing marketplace client for patients and consumers. The Web &
  Backend team did not build this application but defined the API
  contracts it consumes.
- The **Admin Console** is integrated into the SaaS Dashboard under role-
  guarded routes and provides cross-tenant user management and platform
  analytics.

At the **API tier**, a shared Node.js/Express v5 service written in
TypeScript exposes a RESTful interface. Every request passes through a
middleware pipeline consisting of: Helmet security headers, CORS with an
origin allow-list, Morgan request logging, JWT authentication (which
extracts `userId`, `role`, and, for pharmacy managers, `pharmacyId` into
`req.user`), role-based access control middleware (which gates endpoints by
declared roles), and a centralized error handler that standardizes every
error response into the `{ success: false, error: { code, message,
details? } }` envelope documented in the API contract. A tenant gate
pattern injects the tenant context into every downstream service, so
individual controllers never have to re-derive or re-validate it.

At the **data tier**, a MongoDB Atlas cluster stores six collections —
`users`, `medicines`, `inventoryTransactions`, `orders`, `payments`, and
`auditLogs` — each indexed for its dominant query patterns and each
tenant-scoped collection carrying a `pharmacyId` field. Every tenant-
scoped collection has a compound index on `(pharmacyId, ...)` for
efficient isolation queries, and the `medicines` collection additionally
carries a text index on `(name, category, genericName)` to support the
public marketplace search.

### Key Mechanisms

Four mechanisms deserve detailed description because they are the
engineering core of the platform.

**Mechanism 1 — JWT-embedded tenant identity.** At login, the backend
issues a JWT whose payload carries `userId`, `role`, and (for
`pharmacy_manager` users) `pharmacyId`. Every subsequent request presents
this token; the authentication middleware verifies it, decodes the
payload, and attaches the decoded fields to `req.user`. Tenant-scoped
services then filter every query by `req.user.pharmacyId`, and client-
supplied `pharmacyId` values are ignored. This makes tenant isolation a
property of the middleware pipeline rather than of individual endpoints,
and makes the backend stateless — it can be scaled horizontally without
session storage.

**Mechanism 2 — Atomic stock deduction with FEFO batch selection.** When
a pharmacy manager approves an order, the backend enters a database
session and, for each order item, performs an atomic `findOneAndUpdate`
with an `$inc` operator guarded by a `$gte` condition on the medicine's
`totalStock`. This operation either decrements stock by exactly the
requested quantity or fails — it cannot produce negative stock, and it
cannot race against a concurrent approval. The updated medicine's batch
array is then sorted by `expiryDate` ascending, and stock is deducted from
the earliest-expiring batches first (FEFO), with one immutable GIN ledger
entry created per batch touched. All of this happens inside the same
session, so it is committed or rolled back atomically.

**Mechanism 3 — Schema-level immutability.** The `auditLogs` and
`inventoryTransactions` collections declare Mongoose pre-hooks that
intercept every update, replace, and delete operation and throw an
"immutable — forbidden" error. This means that even a buggy controller
or a future refactor that accidentally issues a mutation against one of
these collections will fail at the database layer. Immutability is
therefore a property of the schema, not a convention enforced by code
review.

**Mechanism 4 — Centralized audit logging with before/after snapshots.**
A single `logAction()` utility is called from every data-modifying
controller. It captures the request's actor identity, IP address, and
User-Agent; accepts `before` and `after` document snapshots from the
caller; derives the tenant `pharmacyId` from the audited resource; and
inserts an immutable audit record inside the same transaction as the
business operation. Every auditable action in the system — create, update,
delete, approve, reject, GRN, GIN, payment — passes through this single
function, which is the reason the audit trail is complete.

### The Public Marketplace

The public marketplace search is implemented as a MongoDB aggregation
pipeline that joins `medicines` with their owning `users` (pharmacy)
document, filters inactive pharmacies, optionally filters by city, and
applies pagination after the join so that result counts remain accurate.
The pipeline projects only public-safe fields — medicine name, generic
name, category, price, unit of measure, stock level, pharmacy name,
address, city, and geolocation — and deliberately omits batch-level
operational data, internal SKUs, reorder thresholds, and audit history.
The endpoint requires no authentication, so it is the one surface of the
platform available to anonymous visitors.

### The SaaS Dashboard

The frontend SaaS dashboard is organized into feature-based modules —
`auth`, `dashboard`, `inventory`, `orders`, `payments`, `reports`,
`users`, `marketplace`, `audit`, and `admin` — each with its own
`components/`, `hooks/`, `pages/`, `services/`, and `types.ts` sub-tree.
Every data-consuming view uses a custom hook that encapsulates loading,
error, and refresh state, and renders one of three states: a skeleton
loader during fetch, an error panel on failure, or an empty-state panel
when no data is present. A shared `api.ts` Axios instance attaches the
JWT to every request via a request interceptor and standardizes error
handling via a response interceptor that maps backend error codes to
user-friendly messages through a central `errorMapper` utility.

The visual design follows a consistent "One-Book" glassmorphic language
across the dashboard: a deep green primary palette (#0F8B6C), gold
accents (#DDAA4A), off-white backgrounds (#F7FAF9), backdrop-blurred
card surfaces, and a disciplined typography scale using Source Serif 4
for display headings and Inter for interface and body text.

## Conclusion and Recommendation on the Project

The project delivered what it set out to deliver. All eight specific
objectives (SO-1 through SO-8) were achieved: the platform isolates
tenants provably, manages medicines with batch and expiry tracking,
maintains an immutable GRN/GIN ledger, fulfills cross-tenant consumer
orders with atomic stock deduction and FEFO batch selection, records
payments without overpayment, generates tenant-scoped and platform-wide
reports, maintains a complete audit trail, and is deployed to production
on three cloud platforms. The requirement traceability matrix in the SRS
is fully covered, and no requirement in the specification remains in an
"unimplemented" state.

The platform's principal **strengths** are its defense-in-depth approach
to tenant isolation, its schema-level enforcement of immutability, and
its specification-driven development process, which kept intention and
implementation aligned throughout the six-week build window. Its
principal **limitations** are:

- The absence of an automated unit and integration test suite, which makes
  regression detection manual and expensive;
- The absence of a password-change and email-verification flow for
  production-grade account security;
- The absence of a two-factor authentication layer for administrator and
  pharmacy-manager accounts;
- The absence of real payment-gateway integration (payments are recorded
  manually by the pharmacy manager rather than processed online);
- The absence of staff sub-accounts within a pharmacy tenant — today,
  one user account equals one pharmacy tenant, which limits multi-staff
  pharmacies.

Based on these observations, the following **recommendations** are made
for the continued development of Alyah Pharma Net:

1. **Add an automated test suite** covering at minimum the tenant
   isolation property, the atomic stock deduction path, and the
   immutability of the audit and ledger collections. This is the single
   highest-leverage improvement available and should be the next
   engineering milestone.
2. **Integrate a real payment gateway** (e.g., Chapa or SantimPay for
   the Ethiopian market) so that consumer payments can be processed
   online rather than recorded manually, closing the last manual step in
   the order lifecycle.
3. **Add staff sub-accounts** within each pharmacy tenant so that
   multi-employee pharmacies can operate with distinct pharmacist,
   cashier, and manager logins sharing one tenant.
4. **Implement two-factor authentication** for administrator and
   pharmacy-manager accounts, given the sensitivity of the operational
   and financial data the platform holds.
5. **Integrate EFDA GS1 reporting** so that the GTIN and batch data
   already captured by the platform can be exported in the format the
   regulator expects, turning compliance from a side-effect into a
   deliverable.

In conclusion, the project demonstrates that a disciplined,
specification-driven approach — anchored by a small set of governing
documents and enforced through peer review and a protected main branch —
can produce a production multi-tenant SaaS platform with regulatory-grade
data integrity within the timeframe of a single internship. The delivered
system is live, is in active use for demonstration purposes, and provides
a credible foundation on which the recommendations above can be executed
in subsequent development cycles.