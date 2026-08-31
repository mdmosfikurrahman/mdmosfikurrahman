<h1 align="center">Md. Mosfikur Rahman</h1>

<p align="center">
  <b>Software Engineer II — Backend Architecture</b><br/>
  Distributed systems · Rule-driven platforms · Applied machine learning<br/>
  <sub>Dhaka, Bangladesh</sub>
</p>

<p align="center">
  <a href="https://mdmosfikurrahman.github.io">Portfolio</a> &nbsp;·&nbsp;
  <a href="https://mdmosfikurrahman.github.io/resume/">Résumé</a> &nbsp;·&nbsp;
  <a href="https://www.linkedin.com/in/mdmosfikurrahman">LinkedIn</a> &nbsp;·&nbsp;
  <a href="https://scholar.google.com/citations?user=1GAfMAEAAAAJ">Google Scholar</a> &nbsp;·&nbsp;
  <a href="mailto:mdmosfikurrahman.cse@gmail.com">Email</a>
</p>

---

I design the half of software nobody sees until it breaks — the services, schemas, migrations and
workflows that have to hold a product together once real traffic arrives.

Four years of production engineering in **Java** and **.NET**, alongside **ten peer-reviewed
publications** in applied machine learning. Both threads are the same instinct: build the system, then
insist on evidence that it actually works.

---

## What I'm building now

Backend architecture for **Travilo**, a multi-tenant, multi-brand online travel platform at
**iBOS Ltd.** — a sister concern of Akij Resource Ltd. — serving B2B agencies, B2C travellers and
API/consortium partners, at **10k+ daily users**.

- **Architecture.** A .NET 9 microservice estate — reservation, finance, configuration, notification,
  reporting, user, visa — with deliberate service boundaries, plus three operator panels (admin,
  agency, consumer) on Next.js.
- **Configuration over code.** Rule-driven pricing, markup, discount and refundability logic, so a
  commercial change is a configuration change and not a release.
- **Supplier integration.** Search, revalidation, booking, ticketing, void, refund and reissue flows
  normalised across several GDS and NDC suppliers behind one internal contract.
- **Money paths.** Wallet, credit and hold-balance settlement, where the requirement is not merely
  "works" but *never charges twice and never silently loses a debit*.
- **Leading the work.** Technical lead for the team: architecture and code review, mentoring, sprint
  planning, and on-call production support.

---

## How I work

The habits I care about, because platforms this size are lost or saved by them:

- **Fix the cause, not the symptom.** A failed ticket issuance is traced to the predicate that made a
  guard unreachable, and the blast radius is measured against live data before a line is written.
- **Read the whole file, not the diff.** A pre-existing defect in the code being touched is part of the
  change, not a follow-up ticket.
- **Every message has a reader.** An error surfaced to an operator states what happened, whether money
  moved, and what to do next. Internal type names and stack text belong in the log.
- **Promotion is a discipline.** Staging → pre-production → production, forward only, item-wise, and
  the target branch gets built before the merge — a clean cherry-pick is not a compiling one.
- **Migrations are contracts.** Checksummed, idempotent, audited across every service and environment,
  because a service that skips its own migration fails quietly and much later.

---

## Experience

**Software Engineer II · Backend Architecture — iBOS Ltd.** *(Nov 2024 – present)*
Owned the end-to-end backend architecture of a multi-client OTA SaaS platform on .NET 9, SQL Server
and Kubernetes: rule-driven pricing and ancillary logic, supplier orchestration, booking and ticketing
workflows, and a centralised admin surface. Technical lead for the team.

**Software Engineer — REVE Systems Ltd.** *(Jul 2023 – Oct 2024)*
Built the **Customs Bond Management System** for Bangladesh's **National Board of Revenue**, digitising
manual customs-compliance processing for garment exporters. Delivered the Legal Case and Utilization
Declaration modules end to end on Spring Boot, Thymeleaf and Oracle; automated BGMEA/BKMEA
synchronisation; hardened authentication with OAuth2 and Spring Security; raised throughput ~25% by
query and access-path tuning.

**Software Engineer — Backend (GraphQL BFF) — BJIT Group** *(Apr 2022 – Jun 2023)*
Backend for **Rakuten** e-commerce and the **Denka** corporate CMS, delivered to Japanese enterprise
review standards. Built GraphQL backend-for-frontend services with resolver batching, cut nested-query
latency through schema stitching and join-path optimisation, and contributed reusable patterns to
internal schema tooling.

---

## Research

**10 peer-reviewed publications** — 3 journal articles, 6 conference papers, 1 book chapter — with
**180+ citations** and **3 as first author**. Work spans applied ML, cybersecurity, health analytics,
agriculture and educational technology.

| Selected work | Venue | Year |
|---|---|---|
| Impact of COVID-19 on mental health: a quantitative analysis of anxiety and depression — *first author* | Current Research in Behavioral Sciences · [DOI](https://doi.org/10.1016/j.crbeha.2021.100037) | 2021 |
| Future City of Bangladesh: IoT-based autonomous smart sewerage — *first author, **IEEE Best Paper Award*** | IEEE WIECON-ECE · [DOI](https://doi.org/10.1109/WIECON-ECE52138.2020.9397950) | 2020 |
| Impactful e-learning framework: a new hybrid form of education | Current Research in Behavioral Sciences · [DOI](https://doi.org/10.1016/j.crbeha.2021.100038) | 2021 |
| Cyber security intruder detection using a deep learning approach | Springer · [DOI](https://doi.org/10.1007/978-3-031-13150-9_42) | 2023 |
| Machine learning-based prediction of COVID-19 for early diagnosis and treatment | Springer Nature · [DOI](https://doi.org/10.1007/978-981-97-1923-5_16) | 2024 |

**Peer reviewer** for *ISA Transactions*, *Journal of King Saud University — Computer and Information
Sciences*, *Natural Language Processing Journal*, *Current Research in Behavioral Sciences*, and three
international conferences.

**Invited speaker** — technical session, 10th IEEE International Women in Engineering Conference
(WIECON-ECE 2024).

---

## Recognition

- **IEEE Best Paper Award** — WIECON-ECE 2020, as first author
- **Winner** — national Data Science Hackathon, Data Science Summit 2021
- **Erasmus+ Exchange Fellowship** — Adam Mickiewicz University, Poznań

---

## Education

**B.Sc. in Computer Science & Engineering** — Daffodil International University · CGPA 3.83 / 4.00
*(2018–2021)*
**Erasmus+ International Exchange** — Adam Mickiewicz University, Poznań, Poland *(2021)*

Certifications: IBM Data Science Professional Certificate (Coursera) · Data Science and Machine
Learning track (DataCamp)

Currently preparing for graduate study in **data-intensive, intelligent software systems** — where the
engineering and the research finally meet.

---

## Technical foundation

| | |
|---|---|
| **Languages** | Java (8–21), C#, TypeScript, Python, SQL |
| **Backend** | Spring Boot, Spring Security, ASP.NET Core, EF Core, JPA, GraphQL, JUnit, Mockito |
| **Data** | SQL Server, Oracle, PostgreSQL, MySQL, MongoDB, DynamoDB, query optimisation |
| **Platform** | Docker, Kubernetes, gRPC, OAuth2 / JWT, CI/CD, Azure, AWS, ELK |
| **Architecture** | Microservices, clean and layered architecture, rule engines (Drools, Camunda), event-driven workflows |
| **Frontend** | Next.js (App Router), React, Tailwind, Ant Design |
| **Research** | Applied ML, model evaluation, feature engineering, experimental design |

---

<p align="center">
  <sub>Good systems are not written once — they are designed, argued over, measured, and maintained.</sub>
</p>

<p align="center">
  <a href="mailto:mdmosfikurrahman.cse@gmail.com">mdmosfikurrahman.cse@gmail.com</a> &nbsp;·&nbsp;
  <a href="https://mdmosfikurrahman.github.io">mdmosfikurrahman.github.io</a>
</p>
