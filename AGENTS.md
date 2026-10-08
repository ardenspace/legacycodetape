# Legacy Code Tape

A playlist channel for people who build software, electronics and machines across imagined worlds.

## Agreed direction
- Start with 1980s–1990s SF cel-animation aesthetics and lo-fi music made with Suno.
- Titles directly describe music/atmosphere. Optional lore belongs in descriptions.
- Do not impose a fixed layout, protagonist, tape numbering or narrative title scheme.
- User references establish visual taste; make original imagery rather than recreating their characters.
- Image generation plus subtle web-composited CRT/indicator effects is the first video direction.
- Build incrementally. No full automation platform, upload pipeline, new backend or asset database yet.

## Planning and handoff
- Read `docs/NEXT_STEPS.md` before continuing. It records completion status, proposed phases, acceptance criteria and unresolved decisions.
- Update its checkboxes as work is actually completed; do not treat proposed defaults as user-approved requirements.

## Implementation
- Python standard library only for the initial prompt tool: `python3 scripts/prompt.py --help`.
- `config/style.json`: stable style direction.
- `references/catalog.json`: explicit text notes sent to Gemma. Local image pixels are NOT sent by the tool.
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
