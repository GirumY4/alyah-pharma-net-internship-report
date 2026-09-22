## The Section of Work and the Reason for the Placement

During the internship period I was placed in the engineering function of
Alyah Software, the enterprise software division of the Alyah Technologies
group, and more specifically within the Web & Backend delivery team of the
intern development group. Under the group's lean, shared-team model, the
engineering function builds and maintains Alyah ERP, the matching and escrow
technology behind the Aezop marketplace, and custom client systems; it is the
unit in which the company's Core Software Engineer role — held by my company
supervisor, Mr. Ermias Antigegn — is anchored, and it was therefore the unit
best able to provide the close technical supervision my internship required.

Three reasons made this section the natural placement for me. First, my
academic background in the Department of Computer Engineering at Bahir Dar
Institute of Technology concentrated on software engineering, database
systems, and networked applications, which correspond directly to the work
the Web & Backend team performs daily. Second, the team's assignment for the
internship cohort — designing and building Alyah Pharma Net, a multi-tenant
SaaS pharmaceutical logistics platform — demanded exactly the full-stack
competence I wanted to develop: RESTful API engineering, multi-tenant
database design, and a production React dashboard. Third, the company's
development culture, in which specifications are written before code and
every change passes peer review, offered an environment in which engineering
discipline could be learned alongside engineering skill. I therefore requested,
and was assigned to, the Web & Backend team, where I remained for the entire
internship under the supervision of Mr. Ermias Antigegn and the academic
mentorship of Siranesh G.

## Work Tasks Executed

My responsibilities grew progressively from module-level implementation to
ownership of complete features and, finally, to production deployment. The
principal tasks I executed were the following.

- **Shared backend API development.** I implemented, in Node.js with
  Express v5 and TypeScript, the authentication and user-management module
  (registration, bcrypt password hashing, JWT issuance with embedded tenant
  identity, role-based access control middleware), the tenant-scoped medicine
  and inventory module (catalogue CRUD, batch and expiry tracking, GRN/GIN
  stock adjustments against an immutable ledger), the cross-tenant order
  module (order placement with pre-flight stock validation, the
  approve-reject-process-ready-delivered fulfillment lifecycle with atomic
  stock deduction), the payment recording module, the reporting module
  (tenant-scoped and platform-wide aggregation pipelines), and the read-only
  audit log query endpoints.
- **Public marketplace API.** I designed and implemented the global
  marketplace search endpoint, an aggregation pipeline that joins medicine
  records with their owning pharmacy, filters inactive tenants, applies city
  filtering before pagination, and withholds sensitive operational fields
  from public responses.
- **Data-integrity engineering.** I wrote the centralized audit logging
  utility that captures before/after state snapshots, actor identity, IP
  address, and User-Agent for every data-modifying operation, and I enforced
  schema-level immutability on the audit log and inventory transaction
  collections through Mongoose pre-hooks.
- **SaaS dashboard development.** On the frontend I built, in React 19 with
  TypeScript and Vite, the feature-based dashboard modules: the tenant
  dashboard with KPI cards and FEFO alerts, the inventory grid with batch
  expansion and slide-out forms, the order fulfillment workspace with a
  status stepper and payment drawer, the reports and analytics pages with
  charts, the public marketplace explorer, the administrator user-management
  console, and the profile settings screens, all wired to the shared API
  through a typed Axios client with centralized error mapping.
- **Documentation.** I co-authored and maintained the project's four
  governing documents — the IEEE 29148-aligned Software Requirements
  Specification, the Software Design Specification, the REST API
  documentation, and the database schema reference — and treated them as the
  source of truth throughout implementation.
- **Code review and consolidation.** I participated in structured peer
  reviews in which parallel implementations of the same module were compared
  against the specification and consolidated into a single production-grade
  version, and I applied the resulting corrections across the codebase.
- **Deployment and operations.** I deployed the backend to Render, the
  frontend to Vercel, and the database to MongoDB Atlas; configured
  environment variables, CORS whitelisting, and health-check endpoints; and
  diagnosed and resolved the build and runtime failures described later in
  this part.

## Engineering Methods, Tools and Techniques Used

The team worked in a specification-driven, iteratively phased manner. Each
module began from a written requirement with acceptance criteria in the SRS,
passed through design in the SDS and API contract, was implemented on a
short-lived feature branch, returned to the team through a pull-request
review, and was merged only when it satisfied the agreed definition of done.
Commits followed the Conventional Commits format, and the repository
maintained a protected main branch with an integration branch beneath it.
The principal tools and techniques I used daily are summarized below.

<!-- table: Principal tools and techniques used during the internship -->
| Category | Tools and Techniques | Purpose in Daily Work |
| --- | --- | --- |
| Version control and collaboration | Git and GitHub; branch strategy; Conventional Commits; pull-request peer review | Traceable, reviewable integration of every change |
| Backend engineering | Node.js, Express v5, TypeScript; modular controller-service-route structure; middleware pipeline (Helmet, CORS, Morgan, centralized error handler) | Stateless RESTful shared API |
| Database engineering | MongoDB with Mongoose v9; indexing; aggregation pipelines ($lookup, $unwind, $facet); sessions and atomic $inc updates; virtual properties; soft deletes | Multi-tenant storage, reporting, and race-condition-free stock mutation |
| Security engineering | Stateless JWT with embedded tenant identity; bcrypt hashing; role-based access control middleware; CORS origin whitelisting; HTTPS | Authentication, authorization, and tenant isolation |
| Frontend engineering | React 19, Vite, TypeScript; feature-based folder architecture; custom data-fetching hooks; Axios interceptors; centralized error mapper; skeleton, empty, and error UI states; MUI design system | Production-grade SaaS dashboard |
| Documentation engineering | IEEE 29148-aligned SRS, SDS, API contract, database schema reference; requirement traceability matrix | Single source of truth and testable requirements |
| Data-integrity engineering | ALCOA+ principles; 21 CFR Part 11 simulation; schema-level immutability pre-hooks; append-only ledgers; FEFO batch selection; GTIN traceability fields | Regulatory-grade auditability |
| Deployment and operations | Render (backend), Vercel (frontend), MongoDB Atlas (database); platform auto-deploy from Git; environment-variable separation; health-check endpoint; post-deployment verification checklist | Repeatable production releases |

## Major Challenges and Problems Faced

The work was demanding, and several significant challenges arose during the
internship.

- **Designing provable multi-tenant isolation.** Because every pharmacy
  operates as a tenant of one shared database, a single scoping mistake in
  any query could expose one pharmacy's commercial data to another. Ensuring
  that the tenant key was derived exclusively from the authenticated token —
  and never from client input — across dozens of endpoints was a persistent
  design pressure.
- **Stock race conditions under concurrency.** Two consumers ordering the
  last units of the same medicine simultaneously could, with naive
  read-modify-write code, drive stock negative or fulfill both orders from
  one physical batch. Guaranteeing correctness under concurrency required a
  deeper understanding of database transactions than I possessed at the start.
- **Enforcing regulatory-grade immutability.** Simulating ALCOA+ and
  21 CFR Part 11 meant that audit logs and stock ledgers had to be tamper-
  proof not merely by convention but by construction; any code path that
  could silently update or delete such a record was a compliance defect.
- **TypeScript strict-mode friction at scale.** As the codebase grew, the
  compiler surfaced large families of type errors — nullable union types
  reaching function parameters, mismatched middleware signatures, and
  response shapes that did not match their declared interfaces — which
  blocked builds and consumed significant time.
- **Frontend integration defects.** Several runtime failures appeared only
  in the browser: a blank inventory screen caused by an undefined pagination
  object, missing component exports that crashed pages at render time, and
  framework warnings from disabled controls wrapped in tooltips. These
  defects taught me that a compiling frontend is not a correct frontend.
- **Production build and environment failures.** The move to cloud hosting
  exposed platform differences that never appear locally: the build service
  omitted development dependencies and therefore all TypeScript type
  packages (error TS2688); the case-sensitive Linux filesystem rejected
  imports whose casing differed from the folder names on my machine (error
  TS2307); a missing database connection variable crashed the server at boot;
  an un-whitelisted frontend origin produced CORS rejections; and a missing
  build-time API base URL variable shipped a frontend that rendered a blank
  page and called its own host for data.
- **Absence of an automated test suite.** Verification relied heavily on
  manual API exercise and browser inspection. While effective for the
  internship's scope, this made regressions expensive to detect and was the
  most important process weakness I identified.

Beyond these technical challenges, the domain itself presented the problem
later selected for project work: medicine discovery in Ethiopian towns still
runs on a "phone call and walk-in" model, and independent pharmacies manage
stock on paper or spreadsheets with no audit trail. The measures below
address the technical challenges; the domain problem is treated as the
project work of Part Four.

## Measures Taken to Overcome the Challenges

Each challenge was met with a concrete engineering measure, most of which
became permanent parts of the platform's architecture.

<!-- table: Challenges, measures taken, and observed results -->
| # | Challenge | Measure Taken | Result |
| --- | --- | --- | --- |
| 1 | Cross-tenant data leakage risk | Tenant key injected only from the verified token by a dedicated middleware; client-supplied tenant values ignored; isolation verified by cross-tenant API tests | Cross-tenant access provably impossible |
| 2 | Stock race conditions | Stock mutation performed with atomic increment operators inside database sessions guarded by a sufficient-stock condition; ledger entries written in the same transaction | No negative stock; fulfillment is all-or-nothing |
| 3 | Tamper-prone compliance records | Schema-level pre-hooks rejecting every update, replace, and delete operation on audit and ledger collections; append-only design | Immutability enforced at the database layer |
| 4 | Strict-mode compile errors | Typed request payloads, explicit null guards, unified middleware signatures, and a single standardized error envelope across all modules | Clean compiler builds locally and in the cloud |
| 5 | Frontend runtime defects | Defensive state initialization, complete feature-level export indexes, and a uniform skeleton-error-empty state pattern in every data view | Stable interface with graceful degradation |
| 6 | Cloud build failures | Forced installation of development dependencies on the build platform; normalized file and import casing to match the case-sensitive filesystem | Reproducible cloud builds |
| 7 | Environment misconfiguration | A documented environment-variable checklist per platform, a health-check endpoint, and a post-deployment verification checklist | Stable production rollout on three platforms |

For the domain problem selected for project work — fragmented medicine
discovery and manual, unaudited pharmacy inventory — the measure taken was
the design and construction of the multi-tenant SaaS platform itself: a
shared backend that isolates each pharmacy's operational data while
exposing a public, cross-tenant marketplace search, backed by immutable
stock and audit ledgers. The analysis, design, and results of that solution
are presented in Part Four.

## Gains in Terms of Improving Practical Skills

The internship converted classroom knowledge into working capability. I can
now design and implement a complete RESTful API module — model, service,
controller, routes, and middleware — and defend each decision against a
written specification; build data-heavy React interfaces with typed service
layers, custom hooks, and professional loading, error, and empty states;
write MongoDB aggregation pipelines and indexed schemas for real reporting
workloads; and take an application from a local repository to a live,
monitored deployment across three cloud platforms. Debugging ceased to be an
emergency and became a method: read the stack, reproduce locally, isolate
the layer, fix the cause, and add the guard that prevents recurrence.

## Gains in Terms of Upgrading Theoretical Knowledge

Theoretically, the internship deepened my understanding of multi-tenancy
models and why shared-schema isolation must be enforced at the application
layer; of transactional integrity and the difference between atomic
database operations and application-level locking; of data-integrity
frameworks (ALCOA+ and 21 CFR Part 11) and how immutability, attribution,
and contemporaneous timestamping are implemented in code; of pharmaceutical
traceability practice, including FEFO batch selection and GTIN barcoding
under the EFDA directive; and of stateless security architecture, in which
the token carries both identity and tenant context so that the server scales
horizontally without session storage.

## Gains in Terms of Improving Team-Playing Skills

Working in a shared repository with a protected main branch taught me that
teamwork in software is mostly communication made durable: clear branch
names, conventional commit messages, pull-request descriptions that explain
intent, and reviews that critique code rather than people. I learned to
split work cleanly with the mobile team by publishing an API contract first,
to accept consolidated rewrites of my own code without friction, and to hold
a shared definition of done rather than a personal one.

## Gains in Terms of Improving Leadership Skills

Although I joined as an intern, module ownership required leadership
behaviour: I presented architectural options to my supervisor with
recommendations and trade-offs, drove the consolidation reviews of parallel
implementations, mentored peers on the tenant-scoping rules once I had
mastered them, and took responsibility for the deployment pipeline that the
whole team subsequently relied upon. I learned that leadership in
engineering is the willingness to be accountable for an outcome rather than
for a task.

## Understanding of Work Ethics, Industrial Psychology and Related Issues

The platform's own design became my lesson in work ethics: every mutation
attributable, every record immutable, every deletion soft and traceable. In
practice I experienced why such discipline exists — because organizations
fail quietly when actions cannot be attributed — and I carried it into my
own conduct: honest reporting of progress and of mistakes, respect for
reviewers' time through small, well-described changes, and punctuality
against sprint commitments. Observing how feedback cycles, supervision
sessions, and shared ownership affected morale gave me a practical
introduction to industrial psychology: teams perform when criticism is safe,
expectations are explicit, and credit is shared.

## Gains in Terms of Entrepreneurship Skills

Alyah Technologies operates as a single pipeline — enterprise software
funding the group, the Innovation Hub supplying trained talent, and the Aezop
marketplace converting talent into paid opportunity — and working inside
that model taught me how a technology business actually creates value. I
learned to read a feature as a cost and a revenue line: tenant onboarding as
the SaaS growth mechanism, pharmacy inventory data as the asset that makes
the marketplace trustworthy, and compliance tooling as a differentiator that
independent pharmacies could never build alone. Designing Alyah Pharma Net
forced me to think in terms of customers, tenants, and unit economics rather
than only in terms of code.

## Gains in Terms of Improving Interpersonal Communication Skills

The internship required me to explain technical decisions to audiences with
different backgrounds: architecture justifications to my company supervisor,
requirement interpretations to teammates, API behaviour to the mobile team,
and business value in plain language during demonstrations. Writing the four
governing project documents sharpened my ability to express constraints and
acceptance criteria unambiguously, while weekly supervision sessions trained
me to receive critique, summarize status honestly, and ask precise questions
instead of speculative ones.

## Recommendation and Conclusion on the Internship Experience

On the basis of this experience I recommend, first, that the company
formalize an automated test suite and a continuous-integration gate so that
the regression burden currently carried by manual verification is removed;
second, that future interns receive a structured one-week onboarding to the
repository, the specification set, and the deployment pipeline, which would
compress the ramp-up time I experienced; and third, that the university
align its project courses more closely with industry tooling — typed
languages, code review, and cloud deployment — so that students arrive
prepared for exactly this environment. For my part, I recommend that
readers of this report treat the internship as I came to treat it: not as a
requirement to satisfy but as a controlled exposure to professional
consequences, where a missing environment variable, an unguarded query, or
an unreviewed merge has real effects and therefore real lessons.

In conclusion, the internship at Alyah Software achieved everything I entered
it hoping for and more. I arrived with theoretical knowledge of databases,
networks, and software design; I left having built, reviewed, deployed, and
defended a production multi-tenant SaaS platform under regulatory-grade data
integrity constraints. The technical skills, the professional habits, and the
understanding of how a software business creates value that I gained in the
Web & Backend team form the foundation on which the project work described
in Part Four — and my future engineering career — now stand.