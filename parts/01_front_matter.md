## Declaration

I, Girum Yasab (ID No. BDU1506302), declare that this internship report is my
original work, prepared under the joint supervision of my university mentor
and my company supervisor at Alyah Softwares. It has not been submitted, in
whole or in part, to this or any other institution for the award of a degree,
diploma, or certificate. All sources of information, ideas, and materials
drawn from other works — including company documents, project specifications,
and technical standards — have been duly acknowledged through citations and
references.

Bahir Dar, Ethiopia — September 21, 2026

Signature: ______________________

Girum Yasab (BDU1506302)

\newpage

## Acknowledgements

First and foremost, I am grateful to God for the strength and clarity to
complete this internship and its report.

I extend my deepest gratitude to Alyah Softwares, my internship hosting
organization, and in particular to my company supervisor, Mr. Ermias Antigegn,
for his patient guidance, professional mentorship, and for trusting me with
real engineering responsibility on the Web & Backend team. Working alongside
the intern development team taught me how software is designed, reviewed, and
shipped in practice.

I sincerely thank my university mentor, Siranesh G., for his consistent
academic supervision, constructive feedback on every draft, and for holding
this work to the standard expected of Bahir Dar Institute of Technology.

I am equally thankful to the staff of the Faculty of Electrical and Computer
Engineering for organizing an internship program that bridges theory and
industry, and to my teammates and colleagues whose daily code reviews and
honest critiques shaped both the platform and this report.

Finally, I thank my family and friends for their unwavering encouragement
throughout this journey.

\newpage

## Executive Summary

This report documents the internship undertaken at Alyah Softwares [6] as a
full-stack intern on the Web & Backend team, and the engineering work
delivered during that period: the design, implementation, and deployment of
**Alyah Pharma Net**, a B2B2C multi-tenant SaaS pharmaceutical logistics
platform [1].

The platform addresses a concrete public-health problem in Ethiopia.
Medicine discovery still operates on a "phone call and walk-in" model [2]:
patients physically visit or telephone pharmacies one by one to locate a
required drug, while independent pharmacies manage stock on paper or
spreadsheets, miss reorder windows, and struggle to demonstrate the
traceability expected by the Ethiopian Food and Drug Authority (EFDA) [12].
Alyah Pharma Net replaces this fragmentation with a centralized digital
marketplace in which each pharmacy operates as an isolated SaaS tenant and
public consumers search live availability across all onboarded pharmacies.

The delivered system consists of a shared Node.js/Express v5 REST API written
in TypeScript, a MongoDB (Mongoose v9) database enforcing tenant isolation
through `pharmacyId` keys extracted from signed JWTs [14], and a React 19 + Vite
SaaS dashboard for pharmacy managers and system administrators. Implemented
modules cover authentication and three-tier role-based access control;
tenant-scoped medicine catalogs with batch, GTIN [13], and expiry tracking;
immutable GRN/GIN stock ledgers; a consumer-to-pharmacy order lifecycle with
atomic stock deduction inside MongoDB transactions; payment recording;
tenant-scoped and platform-wide analytics; and append-only audit logs that
simulate ALCOA+ and 21 CFR Part 11 data-integrity practice [10], [11]. The public
marketplace search aggregates stock across tenants while withholding
sensitive operational fields. The backend is deployed on Render, the
dashboard on Vercel, and the database on MongoDB Atlas.

The work followed a specification-driven process: an IEEE 29148-aligned
Software Requirements Specification [9], a Software Design Specification [2], an API
contract [3], and a database schema reference [4] were authored first and treated as
the source of truth throughout implementation, code review, and testing.
Git/GitHub with conventional commits, peer code review, and iterative
production debugging (build pipeline failures, CORS configuration,
environment management) formed the daily engineering practice.

The internship yielded measurable growth: practical mastery of full-stack
MERN development with TypeScript; theoretical deepening in multi-tenancy,
atomic transactions, and regulatory-grade data integrity; and professional
growth in teamwork, technical communication, and work ethics. Part Two of
this report profiles the hosting organization; Part Three reflects on the
internship experience; Part Four presents the project work in full; and Part
Five concludes with recommendations.

\newpage

\toc

\newpage

\lotf
