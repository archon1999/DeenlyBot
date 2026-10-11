# Frontend architecture

Match the module architecture of the Nexa frontend reference.

```text
src/
  app/                 providers, routes, layouts, theme
  shared/              generic api, ui, hooks, lib, assets
  modules/<feature>/
    application/       index.ts, keys.ts, queries.ts, mutations.ts
    domain/            index.ts, entities/, contracts/, enums/
    data-access/       index.ts, dto/, mappers/, repository/
    ui/                index.ts, pages/<PageName>/, shared/
    index.ts
```

- Flow: UI -> application hooks -> repository contract -> API repository -> HTTP client.
- Domain has no React, UI or transport dependencies.
- API calls and DTO details belong only in repositories and mappers.
- UI never imports the HTTP client; application hooks call repository methods.
- Each layer has a small explicit barrel export.
- Query keys are centralized in `application/keys.ts`; keep one queries and one
  mutations file per module until real complexity justifies splitting them.
- Pages orchestrate feature blocks and routing state. Put feature actions,
  forms and rendering in page-local components rather than monolithic pages.
- Keep reusable feature UI within its module. Global shared code must be
  domain-agnostic and reused across modules.
- Retain Minimal's supplied theme, layouts and component infrastructure.
- Use real Django data, not Minimal demo users, JWT login or mock progress.
- Keep UZ/RU/EN strings complete; Arabic text blocks are RTL, UI is LTR.
- Do not store auth tokens or personal API data in localStorage.
- Verify with typecheck, build, scoped lint and browser smoke checks.

