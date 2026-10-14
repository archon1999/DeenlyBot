# Initial Deenly API contract

All paths below are under `/api/v1/`. JSON DTO keys use snake_case; frontend
repositories map them to domain entities. Personal endpoints resolve the
profile through Django session authentication and never accept a client user ID.
Mutations require CSRF. Lists have server-side language selection from profile.
Current source identity and progress foreign keys stay on `TelegramUser`.

## Reading provenance

Name records, Arabic lesson details, library records and available library analyses
include an additive `provenance` object. Its fields are `kind`, `title`, `url`,
`reference` and `meaning_is_summary`. Clients may receive older responses without
this object and must not invent a source or verification badge.

The object identifies the stored reference, not the author of the local meaning
or an endorsement of the learning explanation. Quran records link to their exact
starting verse; dua references preserve the recorded report/verse citation.
Only recognized, explicitly stored reference numbers are resolved to individual
pages. Other valid source URLs remain as recorded. Unsafe URLs are omitted.

Existing seeded meanings are concise educational renderings. The reader calls
them "Meaning for study" and calls visibly abridged meanings "Concise meaning",
with an explicit notice that they are not full translations. Linguistic analyses
retain their own reference and are distinguished from tafsir. Audio credits and
licenses remain independent and unchanged. No source verification flag is exposed
as a scholarly certification. This presentation change does not rewrite content,
renumber materials, change progress, or require a database migration.

## Auth

- `GET auth/session/`: `{authenticated, profile, bot_username}`. Anonymous profile
  is null; authenticated profile contains `{id, first_name, username, language,
  timezone, account_kind, is_guest, email, telegram_linked}`. `account_kind` is
  `guest`, `member` or legacy `telegram`; email is empty until registered.
  This read also issues a CSRF cookie for login mutations.
- `POST auth/guest/`: `{language?:"uz"|"ru"|"en", timezone?:string}` -> `{profile}`.
  Creates a real session and separate profile with null Telegram ID. Defaults
  are uz/Asia/Tashkent; calling while signed in retains the current account.
- `POST auth/register/`: `{email, password, first_name, language?}` -> `{profile}`.
  Guest or Telegram-only accounts upgrade in place and retain all progress.
  Anonymous registration creates a member. Email is case-insensitively unique;
  first_name is required, max 128; password is 8–128 characters and follows
  Django password validators. Registration does not claim email verification.
- `POST auth/login/`: `{email, password}` -> `{profile}`. Case-insensitive email
  login, Django password hashing, generic invalid-credential errors, throttled.
- `GET auth/profile/`: `{profile}`; `PATCH auth/profile/`:
  `{first_name?, language?, timezone?}` -> `{profile}`. Other fields cannot be
  changed here. first_name must be nonempty/max128; timezone must be valid IANA.
- `POST auth/telegram/start/`: browser-bound, five-minute, single-use challenge;
  returns `{telegram_url, expires_at, verification_code}`. The verified bot
  sender sees the same code through `/start web_<token>` and explicitly
  confirms a request started in their own browser. Opening the link alone
  never approves login. No browser-submitted Telegram ID is trusted.
- `POST auth/telegram/complete/`: pending = HTTP 202 `{status:"pending"}`;
  approved = HTTP 200 `{profile}` and a Django login session; expired/invalid
  is HTTP 400. It resolves only the challenge bound to the browser session.
- `POST auth/miniapp/`: `{init_data}`; verify raw Telegram HMAC and auth_date,
  owner and active state, then establish the same Django session.
- `POST auth/logout/`: end the session.
- `POST auth/telegram/link/start/` and `POST auth/telegram/link/complete/`:
  authenticated browser/account-bound linking with the same URL/expiry/pending
  shapes as Telegram login. Approval still comes only from the verified bot
  sender after explicit bot confirmation showing the destination account.
  Successful complete returns `{profile}`; profile ID may change when
  an empty website identity is reconciled into a legacy Telegram profile.
  Existing email/password Telegram accounts cannot be transferred. If both
  profiles have progress, HTTP409 returns `{code, detail}` and changes no data.
  Conflict codes are `registered_telegram_account`, `both_profiles_have_progress`
  `telegram_already_linked` or `disabled_telegram_account`. Otherwise the profile with progress survives;
  the empty identity is retired without deleting existing foreign keys.

The bot approval adapter enables real browser login without BotFather OIDC
credentials. The existing production bot will need the updated handler when
this release is deployed; do not start a second local polling process with its token.
Website guest/member permissions use the active session's own profile; they do
not bypass the personal-mode guard for Telegram bot approval or Mini App identity.
Website-only profiles never enqueue Telegram notifications without a linked ID.
Auth throttles ignore client forwarding headers and use the direct HTTP ingress
address; counters use local per-process cache in the single-worker personal deployment.

## Names

Name DTO: `{id, order, arabic, transcription, meaning, description, status,
is_next, audio_tracks}`. Status is `new`, `learning` or `learned`.

- `GET names/`: `{results, total, introduced_count, learned_count, due_count,
  next_id}`. Preserve the actual existing dataset and numbering.
- `POST names/<id>/confirm/`: `{created}`. Confirm only the sequential next name.
- `POST names/quiz/`: `{extra_practice?:boolean}`; returns `{question,
  required_names:4}`. question is null until four names have been introduced.
- `POST names/quiz/<uuid>/answer/`: `{selected_option}`; returns QuizResult.

Quiz DTO (names, Arabic and library): `{id, prompt, quiz_type, options:[{label}], audio_tracks}`.
No answer key or target details are sent before submission.
QuizResult: `{accepted, is_correct, correct_option, answer_label, answer_meaning}`.
An answered UUID is idempotent and returns its stored result.

## Arabic

Lesson DTO: `{id, slug, category, order, title, summary, estimated_minutes,
status, preview_arabic}` where status is `new`, `in_progress` or `completed`.
`preview_arabic` is an array of the first two real curriculum item strings.
Item DTO: `{id, arabic_text, transcription, meaning, explanation, item_type,
quran_reference, quran_passage, audio_tracks}`. `quran_passage` is a resolved
published `{id, kind}` library target or null; the narrowest containing passage
is chosen, so a lesson about 1:5 can open the existing Fatiha surah rather than
creating a duplicate ayah. `quran_reference` is a library cross-reference,
not a copied version of the passage or independent progress identity.

- `GET arabic/`: `{lessons, stats, categories}`; category rows are
  `{key, title, description}` in the profile's language. Keys are `alphabet`,
  `quran_vocabulary`, `grammar` (Nahv), `prayer_arabic`, `sarf`, `daily_phrases`,
  `listening`. Existing lesson and progress IDs are preserved. Stats also include
  `audio_count`, the count of introduced items with eligible real audio.
- `GET arabic/lessons/<id>/`: Lesson DTO plus `{explanation, items}`.
- `POST arabic/lessons/<id>/start/`: `{status}`.
- `POST arabic/lessons/<id>/complete/`: `{status}`.
- `POST arabic/quiz/`: `{extra_practice?:boolean, mode?:"text"|"listening"}`
  -> `{question}`. Text mode is the backwards-compatible default. Listening
  mode uses `audio_arabic` or `audio_meaning`, four distinct options drawn only
  from this user's introduced, published, audio-enabled materials. It returns
  null when there are fewer than four suitable candidates. The prompt is a
  localized listening instruction, never the answer; audio segment captions
  and content labels are omitted from the quiz snapshot. Listening answers use
  the same owner-scoped, idempotent spaced-repetition rules as text answers.
- `POST arabic/quiz/<uuid>/answer/`: `{selected_option}` -> QuizResult.

## Library

LibraryItem DTO: `{id, kind, title, arabic_text, transcription, translation,
reference, is_favorite, is_studied, audio_tracks}`. kind is `ayah`, `surah` or `dua`.

- `GET library/?kind=ayah|surah|dua|favorites&page=1&q=...`:
  `{results, count, page, pages}`, ten entries per page.
- `POST library/<kind>/<id>/favorite/`: `{saved:boolean}` -> `{saved}`.
  This sets the requested state and is idempotent, not a toggle.
- `GET library/<kind>/<id>/`: LibraryItem DTO plus `analysis`, either null or
  `{summary, context, explanation, verses:[{key, arabic_text, translation,
  transcription, words:[{id, arabic_text, root, meaning, transcription,
  grammar_note}]}]}`. Only published materials and verified source-backed
  analyses with complete verse translations in the requested language appear.
  Canonical verse keys and lexical identities are shared across passages;
  grammar notes cover explicitly selected vocabulary, not an invented full
  tafsir. The reader's text, linguistic analysis and practice are distinct.
- `POST library/<kind>/<id>/study/`: `{created, is_studied:true}`. Explicitly
  introduce a published material; replaying never resets its review schedule.
- `GET library/practice/?kind=ayah|surah|dua|favorites`: `{stats}` with
  `{total_count, studied_count, due_count, answers, accuracy, audio_count}` for the selected
  collection; total includes all published items independently of list search/page.
- `POST library/quiz/`: `{kind?, extra_practice?:boolean, mode?:"text"|"listening",
  item_id?:number}` -> `{question}` using
  the Quiz DTO above. Types: `arabic_meaning`, `meaning_arabic`, `arabic_title`,
  `title_arabic`. Four unique options come only from this user's studied,
  published items in that collection (favorites includes only saved items).
  Missing/ambiguous content is excluded; fewer than four suitable items yields
  null. The target is the earliest review, or random in extra-practice mode.
  An optional `item_id` selects a studied material for in-reader practice; an
  unstudied or outside-collection target is rejected. Listening mode adds
  `audio_arabic` and `audio_meaning`, requiring four eligible, studied audio
  candidates in the same collection; text remains available without audio.
- `POST library/quiz/<uuid>/answer/`: `{selected_option}` -> QuizResult.
  Answers are owner-scoped and idempotent; correct/incorrect answers advance
  the shared spaced-repetition schedule. Extra practice records accuracy but
  does not move the next-review date. Questions snapshot their language and
  answer text; changing locale or editing content cannot change the answer key.

### Shared audio

AudioTrack DTO: `{id, label, voice, url, duration_ms, segments:[{key, label,
start_ms, end_ms}], attribution, source_url}`. `id` is opaque; duration may be
null and segments may be empty. Playback is never evidence of learning and does
not write a user's progress. Names, Arabic items and library materials reuse
the same independent recording records. Multi-verse passages may have one
track per verse; incomplete ranges do not imply a complete recording.

Only published, available, rights-confirmed and pronunciation-verified real
recordings are exposed. Missing/expired audio returns `[]`, not a fabricated
URL or synthetic Quran recitation. Audio labels are translated into UZ/RU/EN;
attribution stays on the regular player. Quiz audio snapshots remove segment
captions, source labels and identifying content captions. External recording
availability is independent of lesson/progress state.

## Worship

CurrentQada DTO: `{key, source, prayer_date, prayer_type}`, source manual/historical.
Only fajr/dhuhr/asr/maghrib/isha are supported.

- `GET qada/`: `{current, manual_pending, manual_completed,
  historical_completed, historical_configured, fast_balance, manual_queue,
  history}`. current may be null; history/queue records include dates and prayers.
- `POST qada/configure/`: `{start_date, start_prayer}` -> summary.
- `POST qada/add/`: `{prayer_date, prayer_type}` -> summary.
- `POST qada/complete/`: `{expected_key}` -> summary. Reject a stale key.
- `POST qada/fast/`: `{action:"add"|"complete", amount?:number,
  operation_id:<UUID>}` -> summary. Replaying the same operation does not change
  the debt twice; reusing its ID with different intent is rejected.

## Calendar and reports

- `GET calendar/`: `{events:[{id, date, hijri_year, title, description,
  is_estimated}]}` from existing calendar service.
- `GET reports/`: `{stats, weekly_reports}`. stats includes `{names_total,
  names_introduced, names_learned, names_due, total_answers, correct_answers,
  accuracy, arabic_lessons_completed, arabic_lessons_total,
  arabic_items_introduced, arabic_due, qada_completed}`. Accuracy is 0..100.
  Weekly reports include `{id, period_start, period_end, data}`; reads do not
  regenerate or write a report.
- `GET dashboard/`: `{next_name, next_arabic_lesson, reviews_due,
  arabic_reviews_due, stats, qada, upcoming_events}` using the above DTOs.
  `upcoming_events` includes all events from today through six calendar months
  ahead, inclusive, using the profile's timezone (month-end dates are clamped).
  The full calendar endpoint retains its longer 400-day window.

## Settings

- `GET settings/`: `{language, timezone, enabled, random_messages_per_day,
  random_window_start, random_window_end, weekly_report_enabled,
  weekly_report_weekday, weekly_report_time}`.
- `PATCH settings/`: validated fields from the same shape -> current settings.
  Preserve the half-hour schedule and sent/queued quota; replan after commit.

Form errors are HTTP 400 with field errors or `{detail}`. Stale/conflicting
domain commands may use 409. The frontend displays server feedback and keeps
values available for correction. HTTP 403 from session authentication must not
be retried indefinitely. Query caches are invalidated after accepted mutations.
