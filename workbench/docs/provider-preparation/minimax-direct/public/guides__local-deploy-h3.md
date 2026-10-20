> ## Documentation Index
> Fetch the complete documentation index at: https://platform.minimax.io/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Run and self-host MiniMax H3

> Run MiniMax H3 locally with ComfyUI or deploy a reproducible H3-Base service with SGLang.

<Warning>
  MiniMax H3 is governed by the [MiniMax H3 Community License Agreement](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE). As of the license revision reviewed on August 26, 2026, the United States, European Union, United Kingdom, and South Korea are Excluded Territories and require a separate license. Review the current agreement before downloading, deploying, or offering a hosted service.
</Warning>

MiniMax H3-Base jointly generates 768p video and synchronized stereo audio. This page provides two distinct paths: a visual local workflow with ComfyUI and a self-hosted API service with SGLang on NVIDIA data-center GPUs.

## Status and scope

| Item | Pinned baseline |
| :- | :- |
| SGLang deployment status | **Preview** — H3 support ships in SGLang v0.5.17 and later on PyPI; this page pins a source commit for reproducibility, and the upstream diffusion install still uses `--prerelease=allow` for its dependencies |
| vLLM-Omni support | Community-maintained recipe on vLLM 0.26.0; see [Self-host with vLLM-Omni](#self-host-with-vllm-omni) |
| ComfyUI support | Native T2V, I2V, and R2V templates in ComfyUI `0.30.0` or later; uses converted Comfy-Org weights |
| Last reviewed | August 26, 2026 |
| Model | [`MiniMaxAI/MiniMax-H3`](https://huggingface.co/MiniMaxAI/MiniMax-H3), revision `42ed227ee7df40d41602854ae760620d6eb651fe` |
| Inference framework | SGLang source commit `2511743bd784e69e5a81ca3d926a000711dae4ab` |
| SGLang Quickstart checkpoint | FL2VA, official mixed BF16/FP32 weights |
| SGLang Quickstart hardware | One node with 8 × NVIDIA B200, Ulysses degree 8, resident components |
| API verified by the upstream recipe | Asynchronous `/v1/videos` endpoint, 5-second T2VA at a 768-pixel short edge |

The pinned commits make the commands repeatable, but H3 diffusion serving is not yet a stable SGLang release contract. Revalidate the page before changing either revision.

<Note>
  The open release contains H3-Base FL2VA and Ref2VA. It does not contain H3-Context-IR or H3-Regenerate-2K. A self-hosted H3-Base service therefore does not reproduce the complete MiniMax Platform Context-IR and 2K workflow.
</Note>

## Choose a deployment path

| Path | Best for | Interface | Weights | Validation boundary |
| :- | :- | :- | :- | :- |
| **ComfyUI local workflow** | Interactive creation, prompt iteration, keyframes, and references | Visual node graph and template library | Pruned and quantized conversions published by Comfy-Org | ComfyUI-native templates; not the same numerical baseline as the official mixed BF16/FP32 checkpoint |
| **SGLang self-hosted API** | Reproducible server deployment and application integration | Asynchronous `/v1/videos` API | Official `MiniMaxAI/MiniMax-H3` checkpoint | Pinned 8 × B200 FL2VA reference in this guide |
| **vLLM-Omni self-hosted API** | Combined FL2VA + Ref2VA service, synchronous MP4 responses, and AMD ROCm hosts | Synchronous and asynchronous `/v1/videos` API | Official `MiniMaxAI/MiniMax-H3` checkpoint | Community-maintained upstream recipe; see [Self-host with vLLM-Omni](#self-host-with-vllm-omni) |

Use ComfyUI when you want to create and adjust a workflow visually on a local workstation. Use SGLang when you need an HTTP service, repeatable server configuration, or application integration.

## Run H3 locally with ComfyUI

ComfyUI natively provides MiniMax H3 nodes and example templates. It is the lower-friction path for trying T2V, I2V, and reference-driven workflows without operating an inference API.

<Warning>
  The ComfyUI templates use pruned and quantized files from [`Comfy-Org/MiniMax-H3`](https://huggingface.co/Comfy-Org/MiniMax-H3), including INT8/NVFP4 components. They are different artifacts from the official mixed BF16/FP32 H3 checkpoint used by the SGLang baseline. Output quality, memory use, and reproducibility can differ; do not mix benchmark claims between the two paths.
</Warning>

### ComfyUI baseline

| Item | Value |
| :- | :- |
| ComfyUI | `0.30.0` or later |
| Built-in workflows | MiniMax H3 T2V, I2V, and R2V |
| Workflow template revision reviewed here | [`3c1df78`](https://github.com/Comfy-Org/workflow_templates/tree/3c1df78dedcc66c94ec27e0ed8a809ed7742f863) |
| Comfy-Org model revision reviewed here | [`4cc1d817`](https://huggingface.co/Comfy-Org/MiniMax-H3/tree/4cc1d817b6184899b41293954329f576cb5ae86b) |
| Published minimum GPU memory and performance | Not published in the ComfyUI H3 guide; validate the selected workflow on your hardware |

The version and revisions above record the documentation baseline reviewed on August 26, 2026. The Template Library can evolve after that date.

### Quickstart in the Template Library

1. Update ComfyUI to version `0.30.0` or later and start it normally.
2. Open **Template Library** > **Video**.
3. Select **MiniMax H3 T2V**, **MiniMax H3 I2V**, or **MiniMax H3 R2V**.
4. Follow the model-scan pop-up to download the required files. Restart ComfyUI if the model list does not refresh.
5. Set the prompt and any input image, video, or audio references.
6. In **Resolution Selector**, use `0.98` megapixels with a multiple of `32`, or set `1344 × 768` directly for a 16:9 native canvas. Do not use the `1.0` megapixel step: it resolves to `1376 × 768`, above the H3-Base 768 × 1344 pixel-area limit.
7. Queue the workflow. The result should be an MP4 containing a 24 FPS video stream and synchronized stereo audio.

### Choose a workflow

| Workflow | Input and control | Checkpoint family | Native node | Pinned template |
| :- | :- | :- | :- | :- |
| T2V | Text prompt with shots, camera movement, dialogue, sound effects, and music | FL2VA | `MiniMaxH3ImageToVideo` without keyframes | [T2V JSON](https://github.com/Comfy-Org/workflow_templates/blob/3c1df78dedcc66c94ec27e0ed8a809ed7742f863/templates/video_minimax_h3_t2v.json) |
| I2V | An input image; optional first and last frames | FL2VA | `MiniMaxH3ImageToVideo` | [I2V JSON](https://github.com/Comfy-Org/workflow_templates/blob/3c1df78dedcc66c94ec27e0ed8a809ed7742f863/templates/video_minimax_h3_i2v.json) |
| R2V | Any supported mix of reference images, video, and audio | Ref2VA | `MiniMaxH3ReferenceToVideo` | [R2V JSON](https://github.com/Comfy-Org/workflow_templates/blob/3c1df78dedcc66c94ec27e0ed8a809ed7742f863/templates/video_minimax_h3_r2v.json) |

T2V and I2V use the FL2VA diffusion model. R2V requires the separate Ref2VA diffusion model; the two files are not interchangeable. In an R2V prompt, refer to inputs in connection order with tags such as `<Picture 1>`, `<Video 1>`, and `<Audio 1>`, then state which reference controls identity, style, motion, camera, or voice.

### Manual model placement

The Template Library download flow is recommended. For an offline or manually managed installation, download the files listed by the selected template from the [Comfy-Org model repository](https://huggingface.co/Comfy-Org/MiniMax-H3) and place them as follows:

| Component | File | ComfyUI directory |
| :- | :- | :- |
| FL2VA diffusion model for T2V/I2V | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | `ComfyUI/models/diffusion_models/` |
| Ref2VA diffusion model for R2V | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | `ComfyUI/models/diffusion_models/` |
| Text encoder | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `ComfyUI/models/text_encoders/` |
| Video VAE | `minimax_h3_video_vae_fp16.safetensors` | `ComfyUI/models/vae/` |
| Audio VAE | `minimax_h3_audio_vae_fp32.safetensors` | `ComfyUI/models/vae/` |
| Optional workflow LoRA | The FL2V 8-step or Ref2V 4-step LoRA requested by the selected template | `ComfyUI/models/loras/` |

For a reproducible team workflow, export the workflow JSON and record the ComfyUI version plus every model-file revision. Do not silently replace the FL2VA model with Ref2VA weights or enable a Turbo LoRA without recording the quality change.

### Resolution, duration, and Turbo mode

* H3-Base uses a 768-pixel short edge and dimensions aligned to a multiple of `32`; `1344 × 768` is the native 16:9 canvas.
* Duration snaps to the model's `17k + 5` frame grid at 24 FPS. A requested duration can therefore be adjusted to a valid frame count.
* The example FL2VA workflow uses 20 steps by default. Its optional 8-step Turbo LoRA is faster but can reduce motion and audio quality.
* The R2V workflow uses a separate optional 4-step Turbo LoRA. Record the LoRA name, strength, steps, seed, and all references when comparing results.

ComfyUI also exposes advanced H3 workflows such as arbitrary-frame guides through `MiniMaxH3AddGuide`, prompt embeddings, and latent noise masks for inpainting or extension. These features and optional Sage Attention acceleration evolve with ComfyUI; follow the [official MiniMax H3 ComfyUI guide](https://docs.comfy.org/tutorials/video/minimax/minimax-h3) before using them in a pinned production workflow.

## SGLang hardware and environment

The 8 × B200 topology below is a reference configuration, not a minimum-hardware claim. The current MiniMax model card demonstrates a four-GPU SGLang command but does not name the GPU model or publish peak VRAM, host RAM, disk, interconnect, driver, CUDA, or latency measurements for that command.

| Requirement | Reference value | Source status |
| :- | :- | :- |
| GPU | 8 × NVIDIA B200 on one node | SGLang-verified topology used by this page |
| Precision and placement | Official mixed BF16/FP32 weights; resident components | SGLang upstream reference path |
| Host RAM | Not published for this exact B200 recipe | Confirm capacity before deployment |
| Local disk | Exact requirement not published; the upstream cookbook reports approximately 108 GB of model weights | Reserve additional space for download metadata and outputs |
| Interconnect | Exact minimum not published | A high-bandwidth single-node GPU topology is recommended |
| OS and Python | Linux and Python 3.12 | This page's source-install environment |
| CUDA and NVIDIA driver | No H3-specific minimum is published | Use versions compatible with B200, PyTorch, and the pinned SGLang commit |

Install `git`, `curl`, `jq`, `ffmpeg`, a compatible NVIDIA driver, and the CUDA runtime before continuing. Do not interpret an unpublished requirement as no requirement.

## SGLang Quickstart

The following flow downloads only the FL2VA partition, starts a loopback-only service, waits for readiness, submits a job, polls it, downloads the MP4, and inspects its streams.

### 1. Install the pinned SGLang source

```bash theme={null}
export MINIMAX_H3_WORKDIR="$PWD/minimax-h3-deploy"
mkdir -p "$MINIMAX_H3_WORKDIR"

git clone https://github.com/sgl-project/sglang.git "$MINIMAX_H3_WORKDIR/sglang"
cd "$MINIMAX_H3_WORKDIR/sglang"
git checkout 2511743bd784e69e5a81ca3d926a000711dae4ab

python3 -m pip install --upgrade uv
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e "python[diffusion]" --prerelease=allow
uv pip install "huggingface_hub==1.28.0"
sglang --version
```

This commit pin replaces the mutable `main`, `dev`, or unversioned prerelease installation commonly used during early H3 support.

### 2. Download the pinned FL2VA checkpoint

```bash theme={null}
export HF_HOME="$MINIMAX_H3_WORKDIR/hf-cache"
export MINIMAX_H3_MODEL_DIR="$MINIMAX_H3_WORKDIR/model"

hf download MiniMaxAI/MiniMax-H3 \
  --revision 42ed227ee7df40d41602854ae760620d6eb651fe \
  --include "model_index.json" "FL2VA/*" \
  --local-dir "$MINIMAX_H3_MODEL_DIR"
```

Keep the repository root as `--model-path`; do not point SGLang at the `FL2VA/` subdirectory. SGLang selects it through `--model-variant fl2va`.

### 3. Start the FL2VA service

Run this command from the SGLang repository with the virtual environment active:

```bash theme={null}
HF_HUB_OFFLINE=1 sglang serve \
  --model-path "$MINIMAX_H3_MODEL_DIR" \
  --model-variant fl2va \
  --num-gpus 8 \
  --tp-size 1 \
  --ulysses-degree 8 \
  --encoder-parallel auto \
  --performance-mode speed \
  --host 127.0.0.1 \
  --port 30010
```

Keep this process running. The first startup loads the model and performs warmup, so readiness can take several minutes.

### 4. Check readiness

In a second terminal:

```bash theme={null}
curl --fail --retry 60 --retry-delay 10 --retry-all-errors \
  http://127.0.0.1:30010/health
```

A ready service returns:

```json theme={null}
{"status":"ok"}
```

`/liveness` only proves that the HTTP process is accepting requests. Use `/health`, which returns HTTP 503 until model warmup is complete.

### 5. Generate, poll, and download an MP4

```bash theme={null}
video_id=$(
  curl -fsS -X POST http://127.0.0.1:30010/v1/videos \
    -H "Content-Type: application/json" \
    -d '{
      "model": "MiniMaxAI/MiniMax-H3",
      "prompt": "At night, three cats perform with tiny brass instruments in a warm living room, with movement synchronized to the music.",
      "seconds": 5,
      "task": "t2va",
      "conditions": [],
      "target": {
        "short_edge": 768,
        "aspect_ratio": "16:9",
        "duration_seconds": 5.0
      },
      "num_outputs_per_prompt": 1,
      "num_inference_steps": 50,
      "flow_shift": 12.0,
      "audio_flow_shift": 3.0,
      "seed": 1101
    }' | jq -r '.id'
)

test -n "$video_id" && test "$video_id" != "null"

while true; do
  job=$(curl -fsS "http://127.0.0.1:30010/v1/videos/${video_id}")
  status=$(printf '%s' "$job" | jq -r '.status')

  case "$status" in
    completed) break ;;
    failed)
      printf '%s\n' "$job" | jq . >&2
      exit 1
      ;;
    *) sleep 5 ;;
  esac
done

curl -fsS -L \
  "http://127.0.0.1:30010/v1/videos/${video_id}/content" \
  -o minimax-h3-t2va.mp4

ffprobe -v error \
  -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels \
  -of json minimax-h3-t2va.mp4
```

The expected result is a non-empty MP4 with one H.264 video stream at 24 FPS and one AAC stereo audio stream at 32 kHz. The 16:9, 768-short-edge profile resolves to 1344 × 768 and approximately 5 seconds.

## Capability and checkpoint matrix

| Model capability | Checkpoint and task | Status in this page |
| :- | :- | :- |
| Text to video and audio | FL2VA, `task: "t2va"` | Covered by the pinned Quickstart |
| First frame, last frame, or both | FL2VA, `task: "fl2va"` | Supported by the model and SGLang upstream; use one or two image conditions with `role: "keyframe"` |
| Image, video, or audio references | Ref2VA, `task: "ref2va"` | Supported by the model and SGLang upstream; requires a separate Ref2VA service |
| Video-to-video | Ref2VA, `task: "ref2va"` | A reference-input form, not a separate task value |
| Context-IR and 2K regeneration | Not included in H3-Base | Requires MiniMax Platform components and is outside this self-hosted workflow |

H3-Base output is 4–15 seconds, with a 768-pixel short edge, 24 FPS video, and 32 kHz stereo audio. Ref2VA accepts up to 9 images, up to 3 video clips, and up to 3 audio clips; see the model card for per-file and combined limits.

To serve Ref2VA, download `"Ref2VA/*"` at the same pinned model revision and start a second service with `--model-variant ref2va` on another port. Do not reuse an FL2VA server for `ref2va` requests.

## SGLang hardware and performance data

Only compare numbers collected with the same checkpoint, request shape, inference steps, flow shifts, and quality level.

| Configuration | Workload | Published result | Validation owner |
| :- | :- | :- | :- |
| 8 × B200, Ulysses 8, resident, lossless | The Quickstart profile | Exact peak VRAM and latency are not published for this exact recipe | SGLang-verified topology; no MiniMax benchmark published |
| 4 × H200, Ulysses 4, resident, lossless | 1344 × 768, 124 frames, 24 FPS, 50 steps, 5-second T2VA | Mean inference latency 75.10 seconds across three prompt/seed pairs | SGLang upstream benchmark |
| 4 × H200, same workload, `quality: "high"` | Audited Cache-DiT path | Mean inference latency 53.70 seconds; SSIM 0.931 and PSNR 28.16 dB versus lossless video | SGLang upstream benchmark; only valid for the exact audited workload |

The tables below reproduce the SGLang upstream benchmarks. They were measured on upstream builds rather than on the exact commit pinned by this page, so treat them as topology and capacity guidance, not as guarantees for the pinned baseline. Unless noted otherwise, the workload is the Quickstart profile: 1344 × 768, 124 frames, 24 FPS, 50 inference steps, 5-second T2VA, one request in flight.

### 8 × B300 precision and encoder placement sweep

A 12-configuration sweep on a single 8 × B300 node with Ulysses degree 8 and resident components, one measured request per cell after one warmup request. FP8 uses online quantization and is approximate; only the BF16 rows are the lossless reference path.

| Checkpoint | Precision | Encoder placement | Inference latency | Peak VRAM per GPU |
| :- | :- | :- | -: | -: |
| FL2VA | BF16 | `auto` | 19.04 s | 83,578 MB |
| FL2VA | BF16 | `fold` | 19.04 s | 83,578 MB |
| FL2VA | BF16 | `replicate` | 19.04 s | 124,158 MB |
| FL2VA | FP8 | `auto` | 18.03 s | 51,926 MB |
| FL2VA | FP8 | `fold` | 18.04 s | 51,926 MB |
| FL2VA | FP8 | `replicate` | 18.04 s | 92,506 MB |
| Ref2VA | BF16 | `auto` | 29.12 s | 83,968 MB |
| Ref2VA | BF16 | `fold` | 29.13 s | 83,968 MB |
| Ref2VA | BF16 | `replicate` | 29.13 s | 124,490 MB |
| Ref2VA | FP8 | `auto` | 27.12 s | 52,816 MB |
| Ref2VA | FP8 | `fold` | 27.12 s | 52,816 MB |
| Ref2VA | FP8 | `replicate` | 27.12 s | 93,396 MB |

At batch size 1, `auto` resolves to the same fold placement, and `replicate` costs about 40 GB of additional peak VRAM without a latency gain. FP8 mainly buys memory headroom on this topology, not speed.

### 4 × H200 topology comparison

Both lossless resident placements on the same four-card H200 host, back-to-back runs with a fixed prompt and seed. The second pair adds `--warmup-resolutions 1344x768` so warmup already covers the served resolution.

| Topology | Warmup | End-to-end latency | Peak VRAM per GPU |
| :- | :- | -: | -: |
| Ulysses 4 | Default | 84.14 s | 94,288 MB |
| TP 2 + Ulysses 2 | Default | 85.51 s | 63,490 MB |
| Ulysses 4 | `--warmup-resolutions 1344x768` | 74.38 s | 94,290 MB |
| TP 2 + Ulysses 2 | `--warmup-resolutions 1344x768` | 78.33 s | 63,490 MB |

Ulysses 4 is the H200 latency default; TP 2 + Ulysses 2 holds peak VRAM about 30 GB per GPU lower and is why that shape remains the 80 GB H100 recipe.

### 4 × H100 topology comparison

Three lossless placements on the same four-card H100 host. The upstream table does not publish the request shape for these rows, so compare them only against each other.

| Topology | Pipeline latency | Peak VRAM per GPU |
| :- | -: | -: |
| TP 2 + Ulysses 2 | 13.25 s | 66.04 GB |
| FSDP + Ulysses 4 | 13.36 s | 57.01 GB |
| TP 4 + Ulysses 1 | 13.86 s | 49.80 GB |

<Warning>
  An upstream issue reviewed on August 26, 2026 ([sgl-project/sglang#34227](https://github.com/sgl-project/sglang/issues/34227)) reports that serving H3 with `--use-fsdp-inference true` can silently produce corrupted video and audio with no server-side errors. Prefer the TP and Ulysses placements above until the issue is resolved, and validate FSDP output before relying on it.
</Warning>

### Cross-node scaling on 2 × 8 × H200

A controlled denoise-stage comparison between a single 8 × H200 node (Ulysses 8) and two nodes with 16 GPUs (Ulysses 8 × Ring 2, InfiniBand between nodes), holding prompt, seed, and step count fixed. Cross-node H3 requires `--encoder-parallel replicate`; the `auto` fold decision is not node-boundary aware.

| Task | Single node (Ulysses 8) | Cross-node (Ulysses 8 × Ring 2) | Change |
| :- | -: | -: | -: |
| T2VA denoise per step | 0.749 s | 0.477 s | −36.3% |
| Ref2VA/V2V denoise per step | 2.572 s | 1.494 s | −41.9% |

The gain grows with sequence length. Cross-node output is deterministic across repeated runs but is not expected to bit-match a single-node run of the same prompt and seed.

### Consumer GPUs and Ascend NPUs

| Configuration | Workload and mode | Published result |
| :- | :- | :- |
| 2 × RTX 5090 32 GB, TP 2 + layerwise offload, lossless | Quickstart profile, 50 steps | 559.67 s end to end (525.05 s denoise, 33.61 s decode), 26.3 GiB sampled peak per GPU |
| 1 × RTX 4090 24 GB, layerwise offload + `kitchen_int8` | Quickstart profile; online INT8 is approximate | About 18 GB GPU peak; latency depends on host RAM and offload bandwidth |
| 8 × Ascend NPU, TP 2 + SP 4, Laser Attention + Cache-DiT | Quickstart profile; Cache-DiT is approximate | 55.07 s end to end |
| 4 × Ascend NPU, TP 2 + SP 2, Laser Attention + Cache-DiT | Quickstart profile; Cache-DiT is approximate | 103.57 s end to end |

Consumer GPU, offload, quantization, AMD, and multi-node recipes evolve independently. Treat them as [SGLang upstream configurations](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3), not as MiniMax-verified hardware, until a MiniMax test matrix is published.

## SGLang weights, cache, and offline deployment

* The official Hugging Face repository is [`MiniMaxAI/MiniMax-H3`](https://huggingface.co/MiniMaxAI/MiniMax-H3). The default cache root is `~/.cache/huggingface`; this page overrides it with `HF_HOME`.
* The mainland China mirror is [`MiniMax/MiniMax-H3`](https://modelscope.cn/models/MiniMax/MiniMax-H3). Revision parity with the pinned Hugging Face commit has not been documented, so it is not used for the reproducible baseline.
* For an air-gapped host, run the pinned `hf download` command on a connected machine, transfer the complete model directory, and verify that `model_index.json` plus the selected `FL2VA/` or `Ref2VA/` directory are present. Start SGLang with `HF_HUB_OFFLINE=1`.
* Interrupted Hugging Face downloads are resumable. Re-run the same command with the same revision. If a cached file is corrupt, use `hf download --force-download` for that pinned revision rather than switching revisions silently.
* Do not download both checkpoint partitions unless the deployment serves both; each partition is an independent service.

## SGLang production and security

The Quickstart listens on `127.0.0.1` and provides no public ingress. To expose a service:

* Put it behind an authenticated reverse proxy or API gateway; require an API key or equivalent identity control.
* Terminate TLS at the ingress and restrict the backend port with a firewall, security group, or private network.
* Apply request quotas, concurrent-job limits, output retention, audit logging, and abuse controls required by the H3 license.
* Mount server-local reference media read-only and allow only dedicated directories. Do not expose arbitrary filesystem paths.
* If an ingress downloads remote image, video, or audio URLs, enforce a domain allowlist, redirect limit, connection/read timeout, maximum bytes, decoded image dimensions, and media duration before passing a local file to SGLang.

Only after those controls are in place should you change the server to `--host 0.0.0.0`. SGLang support does not itself provide the safeguards required by the model license.

## SGLang troubleshooting

| Symptom | Likely cause | Shortest fix |
| :- | :- | :- |
| `/liveness` works but `/health` returns 503 | The model is still downloading, loading, or warming up | Keep the server running and inspect its logs; send generation traffic only after `/health` returns 200 |
| CUDA OOM during load or warmup | The selected placement/topology differs from the reference or another process occupies GPU memory | Stop competing GPU processes and retry the exact 8 × B200 command; otherwise select a measured configuration in the SGLang cookbook |
| Import, CUDA kernel, or operator error | Python, driver, CUDA, or SGLang source differs from the pinned baseline | Create a clean Python 3.12 environment, check out the documented commit, reinstall `python[diffusion]`, and verify driver compatibility |
| NCCL timeout or worker startup failure | GPUs are not mutually reachable or the visible GPU count does not match the parallel degrees | Check `nvidia-smi topo -m` and `CUDA_VISIBLE_DEVICES`; keep the first deployment on one node with 8 visible GPUs |
| Job fails immediately with a task or condition error | The request was sent to the wrong checkpoint partition or has an invalid condition set | Send `t2va`/`fl2va` to FL2VA and `ref2va` to Ref2VA; include at least one reference condition for Ref2VA |
| Model files are missing or corrupted | The download was incomplete or a different revision was mixed into the directory | Re-run the pinned `hf download` command; use `--force-download` if necessary and keep one revision per model directory |
| Job is `completed` but content download fails | The task ID or port belongs to another server, or the job result is no longer available | Query the task on the same host and port, inspect the returned JSON, and download immediately after completion |

## Self-host with vLLM-Omni

[vLLM-Omni](https://github.com/vllm-project/vllm-omni) also serves H3 through an OpenAI-compatible `/v1/videos` API via its community-maintained [MiniMax-H3 recipe](https://github.com/vllm-project/vllm-omni/blob/main/recipes/MiniMaxAI/MiniMax-H3.md). It is an upstream alternative, not this page's reproducible baseline; the SGLang Quickstart above remains the pinned reference path.

| Item | Reviewed baseline |
| :- | :- |
| Status | **Experimental** — community-maintained recipe, reviewed August 26, 2026 |
| Framework | vLLM `0.26.0` with vLLM-Omni; the RTX 5090 validation below used vLLM-Omni `0.26.1.dev14+gae6577ea` |
| API | Synchronous `/v1/videos/sync` returning the MP4 body directly, plus the asynchronous `/v1/videos` job flow |
| Service shape | One combined service can load both the FL2VA and Ref2VA DiTs while sharing the text encoder and VAEs; SGLang requires one service per partition |
| Storage | About 135 GiB on disk per checkpoint partition; keeping both locally needs roughly 270 GiB |
| Host RAM for consumer GPUs | The two-GPU offload recipe requires at least 200 GiB of available system RAM; a 384 GiB host is recommended |
| Hardware paths | Single GPU with CPU offload; 2 × RTX 5090/4090 with TP 2 and distributed layerwise offload; 4 high-memory GPUs without offload; AMD ROCm (gfx942/gfx950) |

Published upstream evidence, transcribed from the recipe. Do not compare these rows against the SGLang tables above unless the workload matches; several use 209 frames instead of the 124-frame Quickstart profile.

| Configuration | Workload | Published result |
| :- | :- | :- |
| 4 × B300, no offload, Ulysses 4, VAE tile parallel 4, regional compile | FL2VA, 1248 × 768, 209 frames, 50 steps | 86.964 s mean client latency, three requests after one warmup |
| Same configuration | Two-video Ref2VA, 1344 × 768, 362 frames | 784.394 s accounted model-stage mean |
| 2 × RTX 5090 32 GB, TP 2 + distributed layerwise offload, eager | T2VA, 1344 × 768, 124 frames, 50 steps | 8 min 38 s client end to end, about 22.6 GiB sampled peak per GPU; single validation run, not a warmed benchmark |
| 4 × MI300X (ROCm), FLASH\_ATTN, Ulysses 4, text-encoder TP 4, VAE tile parallel 4 | T2VA, 1344 × 768, 209 frames, 50 steps | 267.42 s client end to end, mean of three requests after one warmup |
| 4 × H200, SP 4 + text-encoder TP 4, request-scoped `quality` | 1344 × 768, 124 frames, 50 steps | `lossless` median 85.49 s; `high` (Cache-DiT) median 63.36 s, 1.35 ×, SSIM 0.9709 versus lossless |

Operational notes from the recipe: H3 is CFG-distilled, so `--cfg-parallel-size` must stay 1; the H3 VAE supports only its native `tile` parallel mode; pure Ulysses replicates the full DiT on every rank and is not a capacity path for smaller-memory GPUs; and upstream measurements show request co-batching (`--step-execution --max-num-seqs 4`) does not improve H3 throughput for simultaneous large requests. `ffmpeg` and `ffprobe` must be on `PATH`.

## Fine-tune H3 with LoRA using miles-diffusion

[miles-diffusion](https://github.com/radixark/miles_diffusion) publishes an end-to-end LoRA SFT recipe for H3-Base FL2VA, including data preprocessing constraints, a one-command training script, a learning-rate ablation, and an export path back to SGLang serving. It is an upstream training recipe, not a MiniMax-verified baseline; revalidate before production use.

| Item | Pinned baseline |
| :- | :- |
| Training status | **Experimental** — upstream recipe, reviewed at miles-diffusion commit `578d5a571c4924787eb85f0e6eac0de381f3e54f` on August 26, 2026 |
| Base checkpoint | H3-Base FL2VA; the `t2va` recipe trains the video branch only, audio is rolled out but excluded from the loss |
| Recipe | `scripts/run_diffusion_sft_h3_t2va.py`, zero-argument dataset-bound run |
| Reference dataset | [`rockdu/WISA-80K-Practical-Dynamics-254`](https://huggingface.co/datasets/rockdu/WISA-80K-Practical-Dynamics-254), 254 curated windows already on the serving grid |
| Reference hardware | 8 × H200 on one node |
| Recipe defaults | Learning rate 3e-5, weight decay 0.01, LoRA rank 64 / alpha 128, rollout batch 32, `--fsdp-flow-shift 12.0`, `--diffusion-guidance-scale 1.0`, `--sft-offload-encoder` |

Training data must land exactly on H3's serving grid; the encoder rejects anything off-grid:

| Item | Required value |
| :- | :- |
| Canvas | Short edge 768; 16:9 resolves to 1344 × 768 |
| Frame rate | 24 FPS, strictly validated (±0.01) |
| Frame count | `17n + 5` lattice, minimum 107 frames (about 4.46 seconds) |
| Manifest | JSONL with `{"prompt": ..., "metadata": {"video": "clips/clip.mp4"}}`; relative media paths are anchored at the JSONL's own directory |

Start a run:

```bash theme={null}
export WANDB_API_KEY=...                       # without it the recipe submits no wandb flags
python3 scripts/run_diffusion_sft_h3_t2va.py   # downloads the reference dataset on first run and trains
# custom data:      --extra-args "--prompt-data /abs/train.jsonl"
# longer delivery:  --num-epoch 10             # recipe default is 3
```

### Training performance reference

Measured on 8 × H200 with the 254-window reference dataset:

| Stage | Published result |
| :- | :- |
| Encoding | About 15 s per clip per GPU; the first dataset pass stalls about 110 s per rollout on cache misses (230 s for rollout 0), warm from rollout 8 |
| Cache | Content-addressed, about 2 × dataset size, stored in `.sft_cache/` next to the JSONL and reused across runs |
| Encoder residency | With `--sft-offload-encoder`, the roughly 70 GB encoder stays in host RAM and occupies the GPU only during encode bursts |
| Optimizer step | About 31 s per step, 4 steps per encoded batch (`--num-steps-per-rollout 4`) |
| 3 epochs (21 rollouts, 84 steps) | 66 minutes from a cold cache |
| 10 epochs (70 rollouts, 280 steps) | 2 h 50 min cold, 2 h 31 min on a warm cache |

Checkpoints are saved at every epoch boundary and on the final rollout; `iter_N` counts completed rollouts, not optimizer steps. Watch bucketed loss (`--log-loss-sigma-bucket`) rather than the aggregate curve: DiT loss magnitude varies strongly with the drawn noise level.

### Learning-rate ablation

The upstream ablation holds data and configuration fixed (rank 64 / alpha 128, 254 windows × 10 epochs) and reports learning rate as the most sensitive parameter:

| Learning rate | Outcome |
| :- | :- |
| 3e-4 | Collapses |
| 1e-4 | Visible frame degradation |
| 5e-5 | Overfitting signs within the first epoch |
| **3e-5** | **Best result; recipe default** |
| 1e-5 | Underfits, barely differs from base |

### Export and serve the LoRA

Training leaves DCP checkpoints only. Export a single safetensors file plus its `adapter_config.json` sidecar:

```bash theme={null}
python3 scripts/export_lora.py --ckpt-dir <run>/ckpt/iter_0000070 \
  --out my_h3_lora.safetensors --lora-rank 64 --lora-alpha 128
```

SGLang loads the exported adapter directly with `--lora-path`. Keep the sidecar next to the safetensors file: it is looked up in the same directory, and without it alpha falls back to rank, which halves the adapter strength. Record the adapter file, rank, alpha, and base revision before comparing outputs against the unmodified baseline.

## License and system boundary

The [MiniMax H3 Community License Agreement](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE) contains territory, commercial-use, distribution, attribution, hosted-service safeguard, and Acceptable Use Policy terms. The license can change; the linked text is authoritative.

| H3 component | Included in the open release | Role |
| :- | :- | :- |
| H3-Context-IR | No | Converts free-form multimodal context into a structured representation |
| H3-Base FL2VA / Ref2VA | Yes | Generates 768p video with synchronized stereo audio |
| H3-Regenerate-2K | No | Regenerates 2K output using the original context and 768p result |

For the model card, reproducible examples, prompt guidance, and license Q\&A, see the [`MiniMaxAI/MiniMax-H3` repository](https://huggingface.co/MiniMaxAI/MiniMax-H3). For advanced hardware, precision, placement, and performance options, see the [SGLang MiniMax-H3 Cookbook](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3).
