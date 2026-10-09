# Legacy Code Tape

A playlist channel for people who build software, electronics and machines across imagined worlds.

## Project direction
- A playlist channel for people who build software, electronics and machines.
- Music is made with Suno.
- Titles describe music and atmosphere; optional lore belongs in descriptions.
- Visual direction is unset. Begin from the user's next brief.
- Do not carry prior image prompts, scene concepts or preference/evaluation notes into new work.
- Do not record likes/dislikes or infer persistent visual preferences from experiments.
- Build incrementally. No full automation platform, upload pipeline, new backend or asset database yet.

## Planning and handoff
- Read `docs/NEXT_STEPS.md` before continuing. It records completion status, proposed phases, acceptance criteria and unresolved decisions.
- Update its checkboxes as work is actually completed; do not treat proposed defaults as user-approved requirements.

## Implementation
- Python standard library only for the initial prompt tool: `python3 scripts/prompt.py --help`.
- For music prompt requests, use the existing Gemma through `scripts/prompt.py --mode music`. Return Korean situation labels/descriptions and copyable English Suno prompts. Genres vary per request; never assume lo-fi. Pass current request context explicitly; prior runs are not automatically read.
- Generate lyrics only when the user requests them: add `--lyrics` (implies vocals) and `--lyrics-language` when a language is specified. Keep English style prompts and lyrics separate. Without a specified language, follow the brief or default to Korean. `--vocals vocals` alone does not request lyrics.
- `config/style.json`: optional style context; currently empty.
- `references/catalog.json`: optional reference notes sent to Gemma; currently empty. Local image pixels are NOT sent by the tool.
- `references/local/`: user references, local only and ignored by Git.
- `runs/`: requests, raw responses, candidates and copyable English prompts; local only.
- Reuse the existing Gemma endpoint on port 8080. Never stop/restart it or bind a new server there.
- No changes to auto-shorts are required. Keep this project independent.
- No image-generation or Suno API integration is configured. Do not claim otherwise.
- Before any future dev server, check machine and project port rules and inspect the selected port.

## Checks
- Dry-run prompt assembly without services.
- Validate candidate output and save raw responses so failures remain inspectable.
- Real model calls are manual smoke checks, not automated tests.
