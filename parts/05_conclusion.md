## General Conclusion

The internship undertaken at Alyah Software — the enterprise software
division of the Alyah Technologies group [6] — and the project work executed
within it have together achieved everything they were established to
achieve. Placed in the Web & Backend delivery team under the supervision of
Mr. Ermias Antigegn and the academic mentorship of Siranesh G., I entered
the company as a student carrying theoretical knowledge of databases,
networks, and software design, and I left it having designed, implemented,
reviewed, deployed, and defended a production multi-tenant SaaS platform
under regulatory-grade data-integrity constraints.

The project itself, Alyah Pharma Net, addressed a problem of direct public
consequence: medicine discovery in Ethiopian towns still runs on a
"phone call and walk-in" model, independent pharmacies manage stock on
paper or spreadsheets, and neither can produce the batch-level traceability
that the Ethiopian Food and Drug Authority expects [12]. The delivered
platform closes all three gaps with a single architecture — a shared backend
that isolates each pharmacy's operational data through JWT-derived tenant
keys while exposing a public, cross-tenant marketplace search — and it does
so with properties rarely present in student work: provable tenant
isolation, atomic stock deduction inside database transactions, schema-level
immutability on audit and ledger collections simulating ALCOA+ and
21 CFR Part 11 [10], [11], FEFO batch selection aligned with the EFDA
Traceability Directive [12], and a live deployment across Render, Vercel,
and MongoDB Atlas [22], [23]. All eight specific objectives set for the
project were achieved, and no requirement in the governing specification
remains unimplemented [1].

Beyond the artefacts, the internship produced a transformation in how I
work. Practically, I can now carry a feature from written requirement to
production deployment and defend every decision in between. Theoretically,
multi-tenancy, transactional integrity, and compliance-grade data handling
are no longer abstract topics but tools I reach for instinctively.
Professionally, the habits of conventional commits, peer review, protected
branches, and honest status reporting have become my default mode of
operation. The most durable lesson, however, is simpler than any of these:
correctness in engineering is not an event but a discipline — it is produced
by specifications treated as living documents, by immutability enforced at
the schema rather than promised in review, and by errors read as documents
rather than feared as verdicts.

The work also has honest limitations, and naming them is part of its
conclusion. Verification relied on manual API exercise and browser testing
rather than an automated suite; payments are recorded manually rather than
processed through a gateway; each pharmacy tenant currently supports a
single manager account; and account security stops at strong passwords and
role-based access. These limitations are not failures of the internship but
the roadmap it leaves behind, and they are addressed in the recommendations
below.

## Recommendation

### Recommendation on the Platform

- **Add an automated test suite** covering, at minimum, the tenant-isolation property, the atomic stock-deduction path, and the immutability of the audit and ledger collections; this is the single highest-leverage improvement available.
- **Integrate a real payment gateway** suitable for the Ethiopian market, such as Chapa or SantimPay, so that consumer payments are processed online rather than recorded manually.
- **Introduce staff sub-accounts** within each pharmacy tenant so that multi-employee pharmacies can operate with distinct pharmacist, cashier, and manager logins under one tenant.
- **Implement two-factor authentication** for administrator and pharmacy-manager accounts, given the sensitivity of the operational and financial data the platform holds.
- **Provide EFDA GS1 reporting export** [12], [13] so that the GTIN and batch data already captured can be submitted in the format the regulator expects, turning compliance from a side-effect into a deliverable.

### Recommendation to the Hosting Company

- Formalize a continuous-integration gate so that no merge reaches the integration branch without compiled checks and the automated tests recommended above.
- Provide future interns with a structured one-week onboarding to the repository, the four governing specification documents, and the deployment pipeline, compressing the ramp-up period experienced in this placement.
- Preserve the specification-driven culture and the deployment environment checklist born from this internship's production incidents as company-standard runbooks.

### Recommendation to the University and the Department

- Align project courses more closely with current industry tooling — typed languages, code-review workflows, and cloud deployment — so that students arrive prepared for exactly this environment.
- Consider extending or splitting the internship period so that a verification phase, rather than only an implementation phase, fits within the placement.
- Encourage capstone and internship projects to maintain living specification documents and requirement traceability matrices, as these proved to be the strongest quality control in this work.

### Recommendation to Future Interns

- Read the specification before writing code; most "difficult" bugs are requirements misread early and defended late.
- Deploy early and often, so that failures surface in the build pipeline where they are cheap, rather than in demonstration where they are not.
- Treat every error message as a document to be read in full; each incident resolved in this internship — from omitted type packages to case-sensitive imports to a missing environment variable — announced itself precisely before it was understood.
- Keep records of decisions and incidents; an audit trail is as valuable for knowledge as it is for compliance.

In final reflection, this internship converted knowledge into judgment. The
platform is live, its integrity properties are enforced by construction
rather than by intention, and its limitations are documented with the same
care as its achievements. I am grateful to Alyah Technologies for treating an
intern as an engineer with real responsibility, and to Bahir Dar Institute
of Technology for requiring the discipline that made the responsibility
safe to grant. The work submitted here stands as both a record of that
experience and a credible foundation for the development cycles that follow.