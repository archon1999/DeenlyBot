# Deenly frontend

React + TypeScript + MUI, built from the user's supplied Minimal TypeScript v7.4.0 Vite starter. The original license file and vendor archive are retained. Minimal is the UI foundation; all personal data comes from Django.

## Local development

Run the Django API on `127.0.0.1:8001`, then:

```powershell
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api`, `/auth` and `/admin` to Django. API requests use Django session cookies and CSRF protection; no authentication tokens are kept in browser storage.

Guest entry and email/password registration/login use the same Django profile/session model. Registering a guest keeps its existing progress. Guest access depends on the session cookie; register before losing that cookie. Email verification and email password-reset are not provided yet.

Browser Telegram login creates a five-minute challenge and opens the bot's approval link. Compare the displayed code in your browser and bot, then explicitly confirm in the bot. Opening the deep link alone never approves access. The profile page uses an account-bound challenge to link Telegram. The updated bot handler must be running against the same database for either flow. Telegram Mini App login exchanges server-verified raw initData for the same session.

Header and account actions use the same Solar Linear icon family as the CP reference, bundled locally with attribution in `NOTICE.md`. Menus and drawers have flat backgrounds; language choices include local flag assets. The dashboard calendar covers six calendar months and date-entry forms use localized MUI DatePicker.

## Architecture

`app/` composes routing, providers, the Minimal theme and layouts. `shared/` contains domain-agnostic HTTP, language and UI infrastructure. Each feature under `modules/` follows:

```text
ui → application → domain contract → data-access repository → shared/api
```

DTOs and snake_case conversions stay in data-access. Modules expose a small barrel per layer. Pages use feature blocks and application hooks rather than transport calls.

## Verification

```powershell
npm run check:architecture
npm run typecheck
npm test
npm run lint
npm run build
```

The app supports Uzbek, Russian and English. Arabic reading blocks use Amiri with RTL direction, independently of the LTR application layout.
