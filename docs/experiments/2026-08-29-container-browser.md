# Guarded container-browser verification — 2026-08-29

## Objective

Verify that the browser vertical slice can perform bounded Chromium actions
inside the hardened Compose container without exposing typed values, page
content, or URL query data, and without opening unrestricted network access.

## Runtime boundary

- Docker Desktop with WSL 2
- Playwright Python 1.61.0
- Chromium headless shell
- application UID/GID: `10001:10001`
- read-only root filesystem
- all Linux capabilities dropped
- `no-new-privileges` enabled
- PID limit: 128
- browser actions enabled only through Compose
- provider model calls disabled

## Successful approved-host run

The browser navigated to the public `httpbin.org` form and filled its customer
name selector. The result was `completed` for both actions, reported one allowed
network request, zero blocked requests, and zero cloud calls. The response
contained only the selector and sanitized URL path; the typed value and page
content were absent.

## Blocked redirect run

The browser navigated to `example.com` and clicked its outbound link. Navigation
to the approved host completed. The outbound destination was not approved, so
the request was intercepted, the click was reported as `blocked`, and the
aggregate result was `partially_completed`. The result reported one allowed and
one blocked request.

## Private-network rejection

A request approving and navigating to `127.0.0.1` was rejected before browser
startup. It reported zero network requests and identified the loopback address
as prohibited.

## Evidence controls

- navigation query strings and fragments are removed from returned targets;
- page titles are represented only by length and SHA-256;
- typed values and page bodies are not included;
- environment placeholders and sensitive form selectors are rejected;
- downloads, service workers, WebSockets, and WebRTC are disabled;
- each action has a bounded timeout and each run accepts at most 25 actions.

This verification establishes a bounded browser-execution vertical slice. It
does not establish general desktop control, authentication workflows, arbitrary
website compatibility, or permission to access unapproved destinations.
