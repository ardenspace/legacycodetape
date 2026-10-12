# Legacy Code Tape

A playlist channel that travels across eras and imagined worlds, bringing the sounds of each destination into everyday life.

## Project direction
- We can go anywhere: the sounds of each world become the background music of our day.
- Eunoh is the recurring protagonist across eras and worlds. Collect image drafts in `runs/eunoh/drafts/`; only user-selected identity references belong in `runs/eunoh/reference/`. World-specific scenes belong in `runs/eunoh/worlds/`.
- Music is made with Suno.
- Titles describe music and atmosphere; optional lore belongs in descriptions.
- Begin each world and scene from the user's next brief. Use explicitly selected Eunoh images for character continuity; clothing, props and settings may change across worlds.
- Do not carry prior image prompts, scene concepts or preference/evaluation notes into new work.
- Do not record likes/dislikes or infer persistent visual preferences from experiments.
- Build incrementally. No full automation platform, upload pipeline, new backend or asset database yet.

## Planning and handoff
- Read `docs/NEXT_STEPS.md` before continuing. It records completion status, proposed phases, acceptance criteria and unresolved decisions.
- Update its checkboxes as work is actually completed; do not treat proposed defaults as user-approved requirements.

## Implementation
- Python standard library only for the initial prompt tool: `python3 scripts/prompt.py --help`.
- Gemma is for image prompts only, using `scripts/prompt.py`. Pass current scene context explicitly; prior runs are not automatically read.
- Write music/Suno prompts directly with GPT in conversation, not through Gemma. Return Korean situation labels/descriptions and copyable English Suno prompts; never assume a fixed genre.
- Generate lyrics only when requested. Keep English style prompts and lyrics separate; follow the requested language or brief, defaulting to Korean.
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
