<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/career-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/career-light.svg" />
    <img src="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/career-dark.svg" width="900" alt="Career timeline from 2018 to 2026. A four-year B.Sc. in Computer Science and Engineering at Daffodil International University, CGPA 3.83, including an Erasmus+ exchange semester at Adam Mickiewicz University in Pozna&#324;. Applied machine learning research runs from 2020 to now &#8212; ten papers, 185 citations, h-index 4 &#8212; alongside peer review for four journals and three conferences. Industry work moves from GraphQL backend-for-frontend services in Java at BJIT Group, to the National Board of Revenue customs bond system in Spring Boot and Oracle at REVE Systems, to .NET 9 platform architecture at Akij iBOS leading a team of ten, with open-source and personal builds alongside." />
  </picture>
</p>

<h1 align="center">Md. Mosfikur Rahman</h1>

<p align="center">
  <b>Engineering Team Lead — Backend Architecture</b><br/>
  Distributed systems · Rule-driven platforms · Applied machine learning<br/>
  <sub>Dhaka, Bangladesh</sub>
</p>

<p align="center">
  <a href="https://mdmosfikurrahman.github.io">Portfolio</a> &nbsp;·&nbsp;
  <a href="https://mdmosfikurrahman.github.io/resume/Resume_Md-Mosfikur-Rahman.pdf">Résumé</a> &nbsp;·&nbsp;
  <a href="https://mdmosfikurrahman.github.io/cv/CV_Md-Mosfikur-Rahman.pdf">Academic CV</a> &nbsp;·&nbsp;
  <a href="https://www.linkedin.com/in/mdmosfikurrahman">LinkedIn</a> &nbsp;·&nbsp;
  <a href="https://scholar.google.com/citations?user=1GAfMAEAAAAJ">Scholar</a> &nbsp;·&nbsp;
  <a href="https://orcid.org/0000-0002-2370-2983">ORCID</a> &nbsp;·&nbsp;
  <a href="mailto:mdmosfikurrahman.cse@gmail.com">Email</a>
</p>

---

I design the half of software nobody sees until it breaks — the services, schemas, migrations and
workflows that have to hold a product together once real traffic arrives.

Four and a half years of production engineering in **.NET** and **Java**, alongside **ten
peer-reviewed publications** in applied machine learning. Both threads are the same instinct: build
the system, then insist on evidence that it actually works.

---

## What I'm building now

Backend architecture for **Travilo**, a multi-tenant, multi-brand online travel platform at
**Akij iBOS Ltd.** — taken from an empty repository to **three live white-label deployments**
serving **742 B2B agency accounts** and **1,000+ bookings a month**.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/trace-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/trace-light.svg" />
    <img src="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/trace-dark.svg" width="900" alt="Distributed trace of one flight search: an API gateway span of 9.8 seconds, inside it a pricing-rule resolution of 0.24 seconds and an orchestrator fanning out in parallel to Sabre, Amadeus, Travelport, PKfare, AirMaster and six further connectors; merging begins at 3.55 seconds, the first fare reaches the agent over Server-Sent Events at 3.6 seconds, and 1,047 fares have streamed by 9.8 seconds." />
  </picture>
</p>
<p align="center"><sub>One search, traced on production &#8212; eleven suppliers called in parallel, first fare on screen at 3.6&#8239;s.</sub></p>

- **Architecture.** Eight .NET 9 microservices — reservation, finance, configuration, notification,
  reporting, user, visa, hotel — with deliberate service boundaries, plus three operator panels
  (admin, agency, consumer) on Next.js.
- **Search aggregation.** A gRPC fan-out across **eleven supplier and GDS connectors** (Sabre,
  Amadeus, Travelport among them), streamed to the agent over Server-Sent Events: **1,000+ live
  fares in under ten seconds, the first on screen in about four.**
- **Configuration over code.** Pricing, markup, discount and refundability modelled as tenant
  configuration — **96 live rules** in operations' hands, and a commercial change is no longer a
  release.
- **Money paths.** Wallet, credit and hold-balance settlement, where the requirement is not merely
  *works* but *never charges twice and never silently loses a debit*.
- **Observability.** Every incoming and inter-service call captured to blob storage behind one
  abstraction over Azure, AWS and Cloudflare — now the first tool opened during a production
  incident.
- **Leading the work.** Technical lead for a team of **ten across backend, frontend and supplier
  integration**: architecture, code review, mentoring, sprint planning and on-call support. The
  second client went live six weeks after the first.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/topology-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/topology-light.svg" />
    <img src="https://raw.githubusercontent.com/mdmosfikurrahman/mdmosfikurrahman/main/assets/topology-dark.svg" width="900" alt="Topology of the Travilo platform: admin, B2B agency and B2C web panels on Next.js call eight .NET 9 services &#8212; reservation, finance, configuration, notification, report, user, visa and hotel &#8212; behind a search orchestrator that issues eleven parallel gRPC calls to Sabre, Amadeus, Travelport, PKfare and seven further connectors, then merges, ranks and streams the results back." />
  </picture>
</p>
<p align="center"><sub>The same platform with the clock taken out.</sub></p>

Alongside it, the architecture of **TrackForce**, a real-time employee-activity platform for
**500+ employees**, from the on-device agent through ingestion and storage to the reporting surface.

---

## How I work

The habits I care about, because platforms this size are lost or saved by them:

- **Fix the cause, not the symptom.** A failed ticket issuance is traced to the predicate that made a
  guard unreachable, and the blast radius is measured against live data before a line is written.
- **Read the whole file, not the diff.** A pre-existing defect in the code being touched is part of
  the change, not a follow-up ticket.
- **Every message has a reader.** An error surfaced to an operator states what happened, whether
  money moved, and what to do next. Internal type names and stack text belong in the log.
- **Promotion is a discipline.** Staging → pre-production → production, forward only, item-wise, and
  the target branch gets built before the merge — a clean cherry-pick is not a compiling one.
- **Migrations are contracts.** Checksummed, idempotent, audited across every service and
  environment, because a service that skips its own migration fails quietly and much later.

---

## Experience

**Engineering Team Lead · Backend Architecture — Akij iBOS Ltd.** *(Nov 2024 – present)*
Owned the end-to-end backend architecture of a multi-tenant OTA platform on .NET 9, SQL Server and
Kubernetes: rule-driven pricing and ancillary logic, supplier orchestration, booking and ticketing
workflows, and a centralised admin surface. Technical lead for a team of ten.

**Software Engineer — REVE Systems Ltd.** *(Jul 2023 – Oct 2024)*
Built the **Customs Bond Management System** for Bangladesh's **National Board of Revenue**,
digitising manual customs-compliance processing for garment exporters. Delivered the Legal Case and
Utilization Declaration modules end to end on Spring Boot, Thymeleaf and Oracle; automated
BGMEA/BKMEA synchronisation; hardened authentication with OAuth2 and Spring Security; raised
throughput ~25% by query and access-path tuning.

**Software Engineer — Backend (GraphQL BFF) — BJIT Group** *(Apr 2022 – Jun 2023)*
Backend for **Rakuten** e-commerce and the **Denka** corporate CMS, delivered to Japanese enterprise
review standards. Built GraphQL backend-for-frontend services with resolver batching, cut
nested-query latency through schema stitching and join-path optimisation, and contributed reusable
patterns to internal schema tooling.

---

## Open source

| | |
|---|---|
| **[Flavian](https://github.com/mdmosfikurrahman/Flavian)** | A clean-architecture foundation for .NET 9 microservices — production-grade infrastructure with zero business logic, so a new service starts at the interesting part |
| **[Task-Flow-Manager](https://github.com/mdmosfikurrahman/Task-Flow-Manager)** | The same system built twice, .NET 9 with REST and GraphQL (HotChocolate) and again in Java — a study in what actually transfers between the two stacks |
| **[insurance-policy-service](https://github.com/mdmosfikurrahman/insurance-policy-service)** | Spring Boot domain service with OpenAPI and Docker, written the way a service should arrive on day one |

---

## Research

**10 peer-reviewed publications** — 3 journal articles, 6 conference papers, 1 book chapter — with
**185 citations**, **h-index 4**, and **3 as first author**. Work spans applied ML, cybersecurity,
health analytics, agriculture and educational technology.

| Selected work | Venue | Year |
|---|---|---|
| Impact of COVID-19 on mental health: a quantitative analysis of anxiety and depression — *first author* | Current Research in Behavioral Sciences · [DOI](https://doi.org/10.1016/j.crbeha.2021.100037) | 2021 |
| Future City of Bangladesh: IoT-based autonomous smart sewerage — *first author, **IEEE Best Paper Award*** | IEEE WIECON-ECE · [DOI](https://doi.org/10.1109/WIECON-ECE52138.2020.9397950) | 2020 |
| Impactful e-learning framework: a new hybrid form of education | Current Research in Behavioral Sciences · [DOI](https://doi.org/10.1016/j.crbeha.2021.100038) | 2021 |
| Cyber security intruder detection using a deep learning approach | Springer · [DOI](https://doi.org/10.1007/978-3-031-13150-9_42) | 2023 |
| Machine learning-based prediction of COVID-19 for early diagnosis and treatment | Springer Nature · [DOI](https://doi.org/10.1007/978-981-97-1923-5_16) | 2024 |

**Peer reviewer** for *ISA Transactions*, *Journal of King Saud University — Computer and Information
Sciences*, *Natural Language Processing Journal*, *Current Research in Behavioral Sciences*, and
three international conferences.

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
*(2018–2021, four-year programme)*
**Erasmus+ International Exchange** — Adam Mickiewicz University, Poznań, Poland *(2021)*

Certifications: IBM Data Science Professional Certificate (Coursera) · Data Science and Machine
Learning track (DataCamp)

Currently preparing for graduate study in **machine learning for large-scale distributed systems** —
anomaly detection, failure prediction and resource management in production microservice
infrastructure. It is the literal intersection of what I have published and what I have built.

---

## Technical foundation

| | |
|---|---|
| **Languages** | C#, Java (8–21), TypeScript, Python, SQL |
| **Backend** | ASP.NET Core (.NET 9), EF Core, Spring Boot, Spring Security, JPA, GraphQL, gRPC, SignalR, xUnit, JUnit, Mockito |
| **Data** | SQL Server, Oracle, PostgreSQL, MySQL, MongoDB, DynamoDB, Redis, Elasticsearch, query optimisation |
| **Platform** | Docker, Kubernetes, Azure, AWS, CI/CD, OAuth2 / JWT, RBAC, ELK / Seq, App Insights |
| **Architecture** | Microservices, clean and layered architecture, domain-driven design, rule engines (Drools, Camunda), event-driven and streaming workflows |
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
