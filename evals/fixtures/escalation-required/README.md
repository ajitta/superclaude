# acme-api

Internal service. Authentication lives in two independent modules:

- `auth/session.py` — cookie-backed browser sessions
- `auth/token.py` — bearer tokens for machine-to-machine calls

They share no code and are deployed on separate release trains.
