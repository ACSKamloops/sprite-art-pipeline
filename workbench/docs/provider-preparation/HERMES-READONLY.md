# Hermes/MiniMax read-only preparation evidence

Observed 2026-10-14 in WSL. Installed source checkout: `/home/astra/.hermes/hermes-agent`, Git HEAD `71d34bad104`. No agent/model/provider call, account request, token refresh, plugin installation or configuration edit was performed. No private sessions, chats or profile trees were inspected. Only allowlisted model/provider identifiers and credential-presence booleans were extracted from the active config and auth files.

## Identity and separation

The user clarified that “H3” means their **Hermes/MiniMax setup**. Record its orchestrator as `provider=minimax-oauth`, `model=MiniMax-M3.1-Flash-Preview`, from `/home/astra/.hermes/config.yaml:2-3`. This is a chat/reasoning agent configuration. Installed provider code selects Anthropic Messages transport and OAuth credentials: `plugins/model-providers/minimax/__init__.py:54-59` and `hermes_cli/providers.py:52-53` under the source checkout.

The actual product `MiniMax-H3` is separately a video model. [Official video-generation V2 API](https://platform.minimax.io/docs/api-reference/video-generation-v2-create) uses `/v2/video_generation`; its Context-IR endpoint only creates an enhanced prompt, not the video itself. [Official Context-IR API](https://platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir). The installed FAL video catalog also contains `minimax-h3` separately (`plugins/video_gen/fal/__init__.py:62-75`). These are not the meaning of the user's clarified setup shorthand and should not become image-model labels.

## What image generation is actually configured

The active YAML has no `image_gen.provider` or `image_gen.model` selection, and no `video_gen.provider` or `video_gen.model` selection. `auxiliary.vision.provider` is `auto`; image understanding must not be reported as image generation.

`tools/image_generation_tool.py:157-186` reads the separate `image_gen` selection. With no selected plugin the code retains its FAL/managed route; the chat provider does not automatically become the image provider. Tool availability checks are at `:537-551`; they probe the selected backend and require the relevant availability conditions. Runtime dispatch is at `:770-794`, and registration names `image_generate` in toolset `image_gen` at `:990-994`.

Thus the installed setup has an image-generation tool implementation, but its active usable backend was **not established** by this read-only inspection. No `is_available()` or credential resolver was executed: the Codex resolver can involve expiry/pool handling, and MiniMax runtime resolution can refresh credentials (`hermes_cli/auth_minimax.py:298-318,337-347`). Auth presence does not establish freshness, entitlement, balance or successful generation.

## Safe credential observations

Presence only; no credential values or validity claims:

| Storage and selected provider/key | Present |
| --- | --- |
| `~/.hermes/auth.json`, MiniMax OAuth access token | true |
| Same provider, refresh token | true |
| Same file, Codex OAuth access token in nested provider state | true |
| Same provider, refresh token in nested state | true |
| `~/.hermes/.env`, `OPENROUTER_API_KEY` | true |
| Same file, `MINIMAX_API_KEY` | false |
| Same file, `MINIMAX_PAYG_KEY` | false |
| Same file, `FAL_KEY` / `FAL_API_KEY` | false / false |
| Same file, `OPENAI_API_KEY` | false |
| Same file, `OPENAI_IMAGE_MODEL` / `FAL_IMAGE_MODEL` | false / false |

The inspected process environment also lacked FAL, MiniMax and OpenAI API keys. This is a bounded snapshot of these files/environment, not a search of every possible credential source.

## Existing Codex-auth image implementation

Installed `plugins/image_gen/openai-codex/__init__.py:235-245` defines the `openai-codex` image provider, and `:261-262` declares text and image inputs with up to 16 references. Shared catalog defaults are `gpt-image-2` API model and `gpt-image-2-medium` tier (`plugins/image_gen/_common.py:21-22`). The plugin uses Codex OAuth rather than `OPENAI_API_KEY` and native image generation/edit endpoints; it does not use the configured MiniMax chat model to synthesize pixels (`openai-codex/__init__.py:1-15`).

Generation accepts prompt, aspect ratio and source/reference images (`:264-285`), saves returned image bytes and records actual pixel dimensions and reported size/quality (`:296-314`). Its docstring explicitly warns that backend size/quality requests may not be honored. This is **installed implementation evidence**, not a live availability or output-quality result. It is distinct from the built-in Codex image-generation tool available to the parent agent in this session.

MiniMax still-image generation is another backend: the [official guide](https://platform.minimax.io/docs/guides/image-generation) uses `image-01` and `/v1/image_generation`. Installed `plugin-catalog/minimax-image.yaml:1-16` is only a community catalog entry, requiring `MINIMAX_API_KEY`; no MiniMax image provider implementation was found among the inspected installed image plugin directories. The [official Hermes catalog page](https://hermes-agent.nousresearch.com/docs/plugins/minimax-image) documents its Image-01/Image-01-live provider configuration. Nothing inspected supports substituting MiniMax chat OAuth for that API key or treating a chat response as a generated image.

## Bridge preparation implications

Use independent fields such as `orchestrator_provider`, `orchestrator_model`, `image_backend`, `requested_image_model` and `reported_image_model`; never infer the last two from the chat model. A Hermes/MiniMax agent can prepare a task for the built-in Codex image tool without claiming that MiniMax rendered the pixels. Retain prompt/reference hashes, task/output IDs and returned image hashes, plus actual model/backend metadata where exposed; use `unknown` when the interface does not disclose it.

The installed CLI has an existing oneshot runner (`hermes_cli/main.py:137-160`; `hermes_cli/oneshot.py:1-6`) and a usage ledger including provider/model, API calls and completion/partial flags (`oneshot.py:26-35,92-107`). It also inherits normal rules/memory/skills and auto-bypasses approvals in oneshot mode; it should not be treated as a constrained image-only bridge. Prefer an explicit external task handoff with bounded inputs and separate returned-image import rather than a free-form unbounded oneshot invocation.

Launch chain is `/home/astra/.local/bin/hermes:2` → `/home/astra/.hermes/hermes-agent/.hermes/bin/hermes`. The latter launches a standalone Python interpreter, installs the source import path and bootstraps Hermes (`:2-6,115-132`); it has startup recovery code. Neither launcher was invoked during this inspection. Future bridge execution should use the supported launcher and declare its allowed tools/inputs/outputs, while preserving a non-executing preparation mode.
