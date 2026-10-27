# Homepage and Premium plans release

The homepage shows Simulizi Fupi before Simulizi Ndefu. Both reuse the existing
story-card includes. Homepage-only flex layouts center every wrapped row with
160px maximum card widths, 16px horizontal / 20px vertical gaps, 2:3 covers and
two-line title space. Mobile cards shrink when necessary to fit two columns.
Dashboard card layouts are unchanged.

## Plans and payments

| Identifier | Name | TZS | Duration |
| --- | --- | ---: | --- |
| daily | Kila Siku | 1,000 | 24 hours |
| weekly | Kila Wiki | 3,000 | 7 days |
| monthly | Kila Mwezi | 7,000 | 30 days |

`accounts/subscriptions.py` owns prices and durations. Pricing links select a
plan and show the existing M-Pesa / WhatsApp instructions; they never activate
Premium. There is no automated gateway or callback endpoint in this application.

Staff must verify the actual M-Pesa amount and transaction reference before
activating the corresponding plan at `/dashboard/premium/`. The server ignores
browser amounts, validates plan identifiers and records the price, verifier,
reference and access interval. References are normalized and unique, so retries
cannot activate a payment twice, including reuse for a different reader or plan.

New activations use timezone-aware timestamps. Renewals begin after existing
active access, so they never shorten a purchased period. Every access check
rejects subscriptions at the exact expiry timestamp without depending on cron.
The existing `expire_subscriptions` command also supports these timestamps.
Legacy date subscriptions retain their original values and remain valid through
the entire previously purchased end date. No backfill changes their dates.

## Migration and deployment

`accounts.0006_premium_plans` adds two nullable User timestamp columns and creates
`PremiumActivation`. It does not delete, rename or rewrite existing records.

Use the environment-aware **gunicorn-qissa** service. Keep the competing
`qissa.service` disabled; it omits `.env` and incorrectly selects SQLite.

Before deployment, create a protected PostgreSQL custom-format backup with
`pg_dump`, verify it with `pg_restore --list` and `pg_restore --file=/dev/null`,
and retain the current commit and service definition for rollback. Use the
existing server environment to configure PostgreSQL; never commit credentials.

Then, from `/home/django_deploy/qissa`, as `django_deploy`:

```sh
set -a
source .env
set +a
git pull --ff-only origin main
venv/bin/python manage.py check
venv/bin/python manage.py migrate --plan
# Inspect plan and verify backup before the next command.
venv/bin/python manage.py migrate accounts 0006 --noinput
venv/bin/python manage.py collectstatic --noinput
```

As an administrator:

```sh
sudo systemctl restart gunicorn-qissa
sudo systemctl status gunicorn-qissa --no-pager -l
curl --fail --head https://getqissa.com/
curl --fail https://getqissa.com/premium/
sudo journalctl -u gunicorn-qissa --since '5 minutes ago' --no-pager
```

For an application rollback, return to the previous commit and restart
`gunicorn-qissa`. Leave the additive migration and audit data in place; old code
ignores the extra schema. Do not reverse migrations or restore an old database
over newly created production data as a routine rollback.

## Validation

The complete suite passes on the production Python 3.12 runtime: **28 tests**.
This includes 17 new Premium/homepage tests. The old paid-view test fixture now
explicitly marks its paid chapter locked, matching the access path it tests.
Checks and migration consistency checks pass. A private staging database was
used for tests and synthetic browser records.

Chrome checks at 375, 768 and 1440 pixels verified section order, card dimensions,
2:3 aspect ratio, mobile wrapping, centered final rows, three pricing cards and
no horizontal overflow. Daily plan selection displayed the server-owned price
and manual payment instructions. The existing local Python 3.14 template-context
compatibility issue is outside this release; validation uses production Python.

## Files changed

- `accounts/models.py`: precise expiry fields, legacy fallback, payment audit model.
- `accounts/subscriptions.py`: immutable plan catalogue and idempotent staff activation.
- `accounts/migrations/0006_premium_plans.py`: additive migration.
- `accounts/test_subscriptions.py`: plan, expiry, renewal, verification and access tests.
- `accounts/views.py`: timestamp-aware renewal reminder.
- `accounts/management/commands/expire_subscriptions.py`: timestamp-aware expiry.
- `dashboard/views.py`: verified plan activation and audit history context.
- `dashboard/analytics.py`: timestamp-aware subscription metrics.
- `pages/views.py`: validated plan selection and server-owned pricing context.
- `pages/tests.py`: section order, visibility, filters, pagination and pricing tests.
- `stories/tests.py`: correct locked paid-chapter fixture.
- `templates/base.html`: scoped homepage grid and responsive pricing styles.
- `templates/pages/home.html`: shorts first, compact shared cards, both listing links.
- `templates/payment/premium.html`: three-tier pricing and manual checkout instructions.
- `templates/payment/paywall.html`: shared plan-selection entry point.
- `templates/stories/chapter_reader.html`: remove obsolete monthly checkout.
- `templates/shorts/detail.html`: remove obsolete price copy.
- `templates/accounts/dashboard.html`: precise expiry display.
- `templates/dash/premium.html`: staff plan verification, timestamps and payment history.
- `DEPLOYMENT.md`: release behavior, validation and deployment/rollback instructions.
