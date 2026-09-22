## Appendix A — Selected API Endpoints

<!-- table: Core REST endpoints and access roles -->

| Endpoint                   | Method     | Access                  |
| -------------------------- | ---------- | ----------------------- |
| /api/auth/login            | POST       | Public                  |
| /api/medicines             | GET / POST | pharmacy_manager, admin |
| /api/medicines/marketplace | GET        | Public                  |
| /api/orders                | POST       | public_user             |
| /api/orders/:id/status     | PATCH      | pharmacy_manager, admin |
| /api/logs                  | GET        | pharmacy_manager, admin |

## Appendix B — Representative Code Extract

```typescript
// Atomic stock deduction on order approval (orders.service.ts)
const medicineAfter = await Medicine.findOneAndUpdate(
  { _id: item.medicineId, pharmacyId },
  { $inc: { totalStock: -item.quantity } },
  { new: true, session },
);
```

\newpage

## Appendix C — System Screenshots

This appendix presents selected screenshots of the deployed Alyah Pharma Net platform. All captures were taken from the production deployment: the SaaS dashboard and public marketplace at `https://alyah-pharma-net.vercel.app`, served by the shared API at `https://alyah-pharma-net-platform.onrender.com`.

### C.1 Public Marketplace (Unauthenticated Medicine Discovery)

![Public marketplace hero search with category quick-filters](assets/images/shot_marketplace.png)

### C.2 Authentication (SaaS Login)

![Glassmorphic login page of the SaaS dashboard](assets/images/shot_login.png)

### C.3 Pharmacy Manager Dashboard

![Tenant-scoped dashboard with KPI cards, recent orders and FEFO expiry alerts](assets/images/shot_dashboard.png)

### C.4 Inventory Grid with Batch Expansion

![Inventory grid showing stock-health chips and an expanded FEFO batch row](assets/images/shot_inventory.png)

### C.5 Order Fulfillment Workspace

![Incoming orders table with status stepper and approve/reject actions](assets/images/shot_orders.png)

### C.6 Reports and Analytics

![Revenue trend area chart, stock-health donut and top-medicine bar chart](assets/images/shot_reports.png)

### C.7 Administrator User Management Console

![Admin console listing platform users with role badges and status controls](assets/images/shot_admin_users.png)

### C.8 Immutable Audit Log Viewer

![Role-scoped audit trail showing action type, actor and before/after snapshots](assets/images/shot_audit.png)

<!-- Capture checklist — delete this comment once all files exist in assets/images/:
1. shot_marketplace.png   -> /marketplace while logged out
2. shot_login.png         -> /login
3. shot_dashboard.png     -> /dashboard as pharmacy_manager
4. shot_inventory.png     -> /inventory with one medicine row expanded
5. shot_orders.png        -> /orders with the detail drawer open
6. shot_reports.png       -> /reports as pharmacy_manager
7. shot_admin_users.png   -> /admin/users as admin
8. shot_audit.png         -> audit log viewer as admin or manager
Save as PNG, width >= 1280 px, into assets/images/. -->

\newpage

## Appendix D — Production Deployment Configuration

The platform is deployed as three independent cloud components: a stateless Node.js API on Render, a static React bundle on Vercel, and a managed MongoDB cluster on Atlas. This appendix records the hosting assignment, the environment configuration of each platform, and the issues encountered — and resolved — during the production rollout.

<!-- table: Hosting assignment of the three production components -->

| Component          | Provider      | Runtime / Service                                              | Production Address                             |
| ------------------ | ------------- | -------------------------------------------------------------- | ---------------------------------------------- |
| Shared backend API | Render        | Node.js web service (Express v5, TypeScript compiled to dist/) | https://alyah-pharma-net-platform.onrender.com |
| SaaS web dashboard | Vercel        | Static React 19 + Vite build served from the edge CDN          | https://alyah-pharma-net.vercel.app            |
| Database           | MongoDB Atlas | Managed replica-set cluster accessed through Mongoose v9       | Connection string held only in Render secrets  |

### D.1 Backend Environment Variables (Render)

Secret values are stored exclusively in the Render environment panel; none are committed to the repository.

<!-- table: Backend environment variables and their purpose -->

| Variable              | Purpose                                                                                             |
| --------------------- | --------------------------------------------------------------------------------------------------- |
| NODE_ENV              | Switches Express, Mongoose and error handling to production behaviour.                              |
| PORT                  | HTTP port bound by the Express server (Render injects its own value).                               |
| MONGO_URI             | MongoDB Atlas SRV connection string with credentials.                                               |
| JWT_SECRET            | Signing key for authentication tokens (32+ random characters).                                      |
| JWT_EXPIRATION        | Token lifetime, set to 8h per FR-1.5.                                                               |
| CORS_ORIGIN           | Comma-separated allow-list containing the Vercel origin and localhost for development.              |
| NPM_CONFIG_PRODUCTION | Set to false so Render installs devDependencies (typescript, @types/\*) required by the build step. |

### D.2 Frontend Environment Variables (Vercel)

Vite inlines variables at build time, so the value must exist before the build runs.

<!-- table: Frontend build-time environment variables -->

| Variable     | Purpose                                                                                                                                 |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| VITE_API_URL | Base URL of the shared API, e.g. https://alyah-pharma-net-platform.onrender.com/api; consumed by the Axios instance in services/api.ts. |

### D.3 Build and Start Commands

<!-- table: Build and start commands per hosting platform -->

| Platform          | Build Command                        | Start / Output                                          |
| ----------------- | ------------------------------------ | ------------------------------------------------------- |
| Render (backend)  | npm install && npm run build         | npm start (executes node dist/server.js)                |
| Vercel (frontend) | npm run build (tsc -b && vite build) | Static bundle published from the dist/ output directory |

### D.4 Deployment Issues Encountered and Their Resolutions

<!-- table: Issues observed during the production rollout and the corrective action taken -->

| Symptom                                                                          | Root Cause                                                                               | Resolution                                                           |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Build failed with TS2688: cannot find type definitions for express, multer, node | Render omitted devDependencies, which contain all TypeScript type packages               | Added NPM_CONFIG_PRODUCTION=false to the Render environment          |
| Build failed with TS2307: module not found for auditLogs paths                   | Linux file systems are case-sensitive; import casing differed from folder casing on disk | Normalised every import and file name to the exact auditLogs casing  |
| Server crashed at boot: MONGODB_URI is not defined                               | Database connection string was never added to the Render environment                     | Added MONGO_URI secret and redeployed                                |
| Browser blocked API calls with a CORS error after first deploy                   | The new Vercel origin was not present in the backend allow-list                          | Appended the Vercel origin to CORS_ORIGIN and redeployed the backend |
| Frontend rendered a blank page and marketplace calls returned 404                | VITE_API_URL was missing at build time, so Axios targeted the Vercel host itself         | Added VITE_API_URL in Vercel and triggered a fresh build             |

### D.5 Post-Deployment Verification Checklist

- GET /health on the Render URL returns 200 OK.
- Login returns a JWT whose payload carries userId, role and, for pharmacy managers, pharmacyId.
- A pharmacy manager session sees only its own medicines, orders, payments and audit entries.
- The public marketplace endpoint responds without authentication and exposes no tenant-sensitive fields.
- Audit log and inventory transaction collections reject every update and delete attempt.
- Browser console shows no CORS or mixed-content errors on any page.
