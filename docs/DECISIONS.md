# StockAI — Engineering Decisions

## Keep product fixes isolated

Functional bugs should be corrected in focused branches and pull requests. This keeps the production diff understandable and makes validation easier.

## Validate behavior, not only syntax

A successful test suite is useful, but production-oriented changes should also be checked against the relevant live workflow when practical.

## Keep tenant boundaries in the backend

UI visibility is not an authorization boundary. Protected operations must validate the authenticated user's company and role on the server.

## Prefer explicit update contracts

Fields whose accidental default could destroy existing information should be explicit in update schemas and covered by regression tests.
