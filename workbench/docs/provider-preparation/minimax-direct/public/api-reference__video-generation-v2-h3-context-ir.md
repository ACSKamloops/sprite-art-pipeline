> ## Documentation Index
> Fetch the complete documentation index at: https://platform.minimax.io/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Create H3-Context-IR Task

> Deeply interpret multimodal context and generate a structured, semantically enriched video prompt.

<Warning>
  This endpoint only returns an enhanced video prompt. It does not create a video generation task.
</Warning>

H3-Context-IR deeply interprets multimodal context across text, images, audio, and video. It analyzes relationships among the inputs and between those inputs and the intended output, performs complex reasoning, and converts that understanding into a structured representation with richer semantic detail while preserving the user's original intent as much as possible.

<Note>
  H3-Context-IR is a complex system and its implementation is not open sourced. This API can be used both to validate the official Full 2K-Workflow results and in production workflows.
</Note>

<Note>
  After creating the task, use [Query Task](/docs/api-reference/video-generation-v2-query) or [List Tasks](/docs/api-reference/video-generation-v2-list). H3-Context-IR tasks have `task_type=h3_context_ir`; when the task succeeds, retrieve the enhanced prompt from `content.prompt`.
</Note>


## OpenAPI

````yaml api-reference/video/generation/api/v2-video-generation.json POST /v2/h3_context_ir
openapi: 3.1.0
info:
  title: MiniMax API
  description: MiniMax video generation V2 (Hailuo-03) API
  license:
    name: MIT
  version: 2.0.0
servers:
  - url: https://api.minimax.io
security:
  - bearerAuth: []
paths:
  /v2/h3_context_ir:
    post:
      tags:
        - Video V2
      summary: Create H3-Context-IR Task
      description: >-
        H3-Context-IR deeply interprets multimodal context across text, images,
        audio, and video. It analyzes relationships among the inputs and between
        those inputs and the intended output, performs complex reasoning, and
        converts that understanding into a structured representation with richer
        semantic detail while preserving the user's original intent as much as
        possible. This endpoint only returns an enhanced prompt; it does not
        create a video generation task.


        H3-Context-IR is a complex system and its implementation is not open
        sourced. This API can be used both to validate the official Full
        2K-Workflow results and in production workflows.
      operationId: h3ContextIRV2Create
      parameters:
        - name: Content-Type
          in: header
          required: true
          description: Media type of the request body. Set it to `application/json`.
          schema:
            type: string
            enum:
              - application/json
            default: application/json
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/H3ContextIRReq'
            examples:
              Text-to-video (t2va):
                value:
                  model: MiniMax-H3
                  content:
                    - type: text
                      text: >-
                        Epic space-opera theatrical teaser: a female captain
                        stands alone before a massive observation window as the
                        last fleet gathers and jumps away in a blinding flash,
                        the bridge shaking, leaving her behind.
                  duration: 5
                  ratio: '16:9'
              Image-to-video (i2va):
                value:
                  model: MiniMax-H3
                  content:
                    - type: text
                      text: >-
                        Pull focus to the people in the background and add more
                        steam to the ramen bowl.
                    - type: image_url
                      image_url:
                        url: >-
                          https://cdn.hailuoai.com/prod/hailuo_demo/testsets/H3_AA_I2VA/gallery/sr_v17_variants_seed42_43_20260724/inputs/4a3a90bf9100_KDmcbkhzYo5sjjxr9FqcVmWVnzb.png
                      role: first_frame
                  duration: 5
                  ratio: adaptive
              Reference-to-video (r2va):
                value:
                  model: MiniMax-H3
                  content:
                    - type: text
                      text: >-
                        Character speaks: Follow the wind, live free. Leave
                        worries behind, enjoy the moment. Voice timbre follows
                        reference audio 1.
                    - type: video_url
                      video_url:
                        url: >-
                          https://cdn.hailuoai.com/prod/hailuo_demo/testsets/h3_promo_eval_ref2va/gallery/sr_v2p26_trio_seed42_20260724/inputs/297573323635_00_%E8%A7%86%E9%A2%911_YnyRbxEwio_video_20260525_163755_1927e9d3.mp4
                      role: reference_video
                    - type: audio_url
                      audio_url:
                        url: >-
                          https://cdn.hailuoai.com/prod/hailuo_demo/testsets/h3_promo_eval_ref2va/gallery/sr_v2p26_trio_seed42_20260724/inputs/f463d523c5ce_01_%E9%9F%B3%E9%A2%911_RSLcbpzJPo_6%E6%9C%885%E6%97%A5(1).mp3
                      role: reference_audio
                  duration: 5
                  ratio: adaptive
        required: true
      responses:
        '200':
          description: >-
            The create endpoint returns a `task_id`. Use this `task_id` with the
            [Query Task](/api-reference/video-generation-v2-query) endpoint to
            retrieve the task status and result. When the task succeeds,
            retrieve the enhanced prompt from `content.prompt`.


            **Successful Query Task response example**


            ```json

            {
              "task": {
                "id": "426586401755526",
                "model": "MiniMax-H3",
                "status": "succeeded",
                "created_at": 1785702855,
                "updated_at": 1785702884,
                "content": {
                  "prompt": "integrated_multimodal_description: [Shot 1] Cinematic, wide shot with a slow push in on a female captain standing center frame with her back to the camera. She has a slender build and short, swept-back silver hair, wearing a crisp, dark navy-blue futuristic military uniform adorned with rigid silver epaulets. Before her stretches a colossal, curved glass observation window dominating the dimly lit starship bridge. The interior features sleek metallic consoles on the left and right emitting soft cyan light. Outside the window, a massive fleet of dark-grey, heavily armored dreadnoughts and cruisers is assembling against a backdrop of a swirling deep-purple and magenta nebula. The rear thrusters of the distant ships glow intensely with fiery orange light. [Shot 2] At 00:02.800, the camera cuts to a medium close-up of the captain from Shot 1 in profile facing right, while the camera shakes strongly. Her facial features are now visible, revealing a woman in her late forties with sharp cheekbones and a stoic expression. A sudden, blinding flash of brilliant cyan and white light bursts through the window as the fleet outside simultaneously jumps into warp, casting harsh, overexposed illumination across her face. The bridge vibrates violently, causing her shoulders to tense and her uniform collar to tremble. The intense light instantly fades into deep shadow, leaving her completely alone against the newly emptied, pitch-black void of space.\noverall_soundscape: Deep, resonant low-frequency thrumming of ship engines, overlaid with rhythmic, high-pitched electronic beeps from the consoles, followed by a sudden, deafening sub-bass boom and a loud, sizzling crackle as the warp drives engage. The immense acoustic impact causes a heavy, metallic clattering of the bridge panels, which instantly drops off into a stark, quiet mechanical hum.\nnon_diegetic_music: Symphonic orchestral score, beginning with a slow, rising brass and string crescendo that abruptly cuts off, instantly transitioning into a single, sustained, low-register solo cello note with no dynamic swell."
                },
                "duration": 5,
                "usage": {
                  "total_tokens": 9090,
                  "prompt_tokens": 5664,
                  "completion_tokens": 3426
                },
                "ratio": "16:9",
                "task_type": "h3_context_ir",
                "modality": "text"
              }
            }

            ```
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VideoGenerationV2Resp'
        '400':
          $ref: '#/components/responses/Err400'
        '401':
          $ref: '#/components/responses/Err401'
        '402':
          $ref: '#/components/responses/Err402'
        '422':
          $ref: '#/components/responses/Err422'
        '429':
          $ref: '#/components/responses/Err429'
        '500':
          $ref: '#/components/responses/Err500'
components:
  schemas:
    H3ContextIRReq:
      type: object
      description: Request parameters for creating an H3-Context-IR task.
      required:
        - model
        - content
        - duration
      properties:
        model:
          type: string
          description: 'Model name. Currently available: `MiniMax-H3`.'
          enum:
            - MiniMax-H3
        content:
          type: array
          description: >-
            Array of multimodal context describing the intended video and the
            relationships among the inputs. Each element is distinguished by
            `type` (`text` / `image_url` / `video_url` / `audio_url`) and can be
            labeled with a `role`.


            **Every request must include one non-empty `text` item (the prompt
            is required)**; otherwise a parameter error is returned.


            Supported input combinations (corresponding to different generation
            scenarios):

            - **Text-to-video**: a single `text` element only.

            - **Image-to-video, first frame**: `text` + 1 `image_url`
            (`role=first_frame`, or omitted).

            - **Image-to-video, last frame**: `text` + 1 `image_url`
            (`role=last_frame`).

            - **Image-to-video, first & last frame**: `text` + 2 `image_url`
            items with `role` set to `first_frame` and `last_frame`
            respectively.

            - **Reference-to-video**: `text` + any combination of reference
            images (`role=reference_image`), reference videos
            (`role=reference_video`), and reference audio
            (`role=reference_audio`).


            > **Image-to-video and reference-to-video are mutually exclusive**:
            if any `reference_image` / `reference_video` / `reference_audio`
            role appears in content, then `first_frame` / `last_frame` must not
            appear (and vice versa); the two cannot be mixed.


            ---


            **Input media limits** (total request body ≤ 64 MB; use public URLs
            for large files, avoid Base64)


            Image `image_url`:


            | Item | Limit |

            | :--- | :--- |

            | Format | JPG, JPEG, PNG, WEBP, HEIC, HEIF |

            | Single file size | ≤ 30 MB |

            | Width/height range | [256, 5760] px |

            | Aspect ratio (w/h) | [0.4, 2.5] |

            | Count | first frame ≤ 1, last frame ≤ 1, reference images ≤ 9 |


            Video `video_url` (reference scenario only):


            | Item | Limit |

            | :--- | :--- |

            | Container / format | MP4 (`.mp4`), MOV (`.mov`) |

            | Codec | Video H.264/AVC, H.265/HEVC; audio AAC, MP3 |

            | Single file size | ≤ 50 MB |

            | Count | ≤ 3 |

            | Per-clip duration | [2, 15] s; total ≤ 15 s |

            | Width/height range | [256, 5760] px |

            | Aspect ratio (w/h) | [0.4, 2.5] |

            | Frame rate | [23.976, 60] |


            Audio `audio_url` (reference scenario only):


            | Item | Limit |

            | :--- | :--- |

            | Format | WAV, MP3 |

            | Single file size | ≤ 15 MB |

            | Count | ≤ 3 |

            | Per-clip duration | [2, 15] s; total ≤ 15 s |
          items:
            $ref: '#/components/schemas/ContentItem'
        duration:
          type: integer
          description: >-
            Target video duration in seconds. Required, integer. Available
            values: `4`-`15`.
          enum:
            - 4
            - 5
            - 6
            - 7
            - 8
            - 9
            - 10
            - 11
            - 12
            - 13
            - 14
            - 15
        ratio:
          type: string
          description: >-
            Aspect ratio of the target video. Defaults to `adaptive`. Available
            values: `adaptive`, `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`.


            **Text-to-video (t2va, content contains only `text`)**: `ratio` is
            required and cannot be `adaptive`; available values `21:9`, `16:9`,
            `4:3`, `1:1`, `3:4`, `9:16`.


            **Image-to-video (i2va, content contains a `first_frame` /
            `last_frame` image)**: the aspect ratio is determined by the input
            image and `ratio` is always `adaptive`; passing another valid value
            does not error but is ignored and treated as `adaptive`.


            **Reference-to-video (r2va, content contains `reference_image` /
            `reference_video` / `reference_audio`)**: `ratio` is optional and
            defaults to `adaptive`; you may also explicitly specify any of the
            concrete ratios above.
          enum:
            - adaptive
            - '21:9'
            - '16:9'
            - '4:3'
            - '1:1'
            - '3:4'
            - '9:16'
        callback_url:
          type: string
          description: >-
            Callback URL for task status changes. Once configured, the MiniMax
            server first sends a verification request containing a `challenge`
            field (you must return the `challenge` unchanged within 3 seconds to
            complete verification); after verification succeeds, it POSTs an
            update to this URL whenever the task status changes. The push body
            has the same structure as the response of the [Query
            Task](/api-reference/video-generation-v2-query) endpoint.


            Callback `status` values: `queued`, `running`, `succeeded`,
            `failed`, `cancelled`.
      example:
        model: MiniMax-H3
        content:
          - type: text
            text: A boy playing basketball by the sea
        duration: 5
        ratio: '16:9'
    VideoGenerationV2Resp:
      type: object
      properties:
        task_id:
          type: string
          description: ID of the task, used to query the task status and result later.
      example:
        task_id: '424010985738629'
    ContentItem:
      type: object
      required:
        - type
      properties:
        type:
          type: string
          description: Type of the input content.
          enum:
            - text
            - image_url
            - video_url
            - audio_url
        text:
          type: string
          description: >-
            Text prompt, **required**: every scenario must include one non-empty
            `text` describing the desired video. Length is counted by
            characters, with a maximum of 7000 characters per `text`.
        image_url:
          type: object
          description: >-
            Image object when `type=image_url` (see the content description
            above for format / size / dimension / count limits).
          required:
            - url
          properties:
            url:
              type: string
              description: >-
                Image location. Supported: a public URL; `mm_file://{file_id}`
                (reference an existing platform file, e.g. an uploaded file or a
                previous output's file_id); a
                `data:image/<format>;base64,<Base64>` data URI (`<format>`
                lowercase).
        video_url:
          type: object
          description: >-
            Video object when `type=video_url` (reference video, reference
            scenario only; see the content description above for format / size /
            duration limits).
          required:
            - url
          properties:
            url:
              type: string
              description: >-
                Video location. Supported: a public URL; `mm_file://{file_id}`
                (reference an existing platform file's file_id); a
                `data:video/mp4;base64,<Base64>` data URI. Note the total
                request body must be ≤ 64 MB and Base64 inflates size by about
                33%, so use a public URL or mm_file:// for large videos.
        audio_url:
          type: object
          description: >-
            Audio object when `type=audio_url` (reference audio, reference
            scenario only; see the content description above for format / size /
            duration limits).
          required:
            - url
          properties:
            url:
              type: string
              description: >-
                Audio location. Supported: a public URL; `mm_file://{file_id}`
                (reference an existing platform file's file_id); a
                `data:audio/<format>;base64,<Base64>` data URI (`<format>`
                lowercase).
        role:
          type: string
          description: >-
            Position or purpose of the content, conditionally required:

            - `first_frame`: first-frame image (image-to-video; when there is a
            single image and no role is set, it defaults to first_frame).

            - `last_frame`: last-frame image (image-to-video first & last frame,
            must be paired with first_frame).

            - `reference_image`: reference image (reference-to-video).

            - `reference_video`: reference video (reference-to-video).

            - `reference_audio`: reference audio (reference-to-video).
          enum:
            - first_frame
            - last_frame
            - reference_image
            - reference_video
            - reference_audio
    OaiError:
      type: object
      description: >-
        OpenAI-style error response. On error the HTTP status is the real error
        code (401/400/429/402/422/500…) and the body is this object.
      properties:
        type:
          type: string
          description: Always `error`.
          example: error
        error:
          $ref: '#/components/schemas/OaiErrorDetail'
        request_id:
          type: string
          description: Request trace ID (for troubleshooting).
    OaiErrorDetail:
      type: object
      properties:
        type:
          type: string
          description: >-
            Error type:
            `authorized_error`(401)/`bad_request_error`(400)/`rate_limit_error`(429)/`insufficient_balance_error`(402)/`unprocessable_entity_error`(422)/`overloaded_error`(529)/`server_error`(500),
            etc.
        message:
          type: string
          description: >-
            Error detail; the trailing parenthesis holds the internal error code
            (e.g. `... (1004)`).
        http_code:
          type: string
          description: HTTP status code as a string, e.g. `401`.
  responses:
    Err400:
      description: Invalid parameters
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/OaiError'
          example:
            type: error
            error:
              type: bad_request_error
              message: >-
                invalid params, content must include a non-empty text item
                (prompt is required) (2013)
              http_code: '400'
            request_id: 021785229015510a2c883cf675b9804d
    Err401:
      description: Authentication failed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/OaiError'
          example:
            type: error
            error:
              type: authorized_error
              message: >-
                login fail: Please carry the API secret key in the
                'Authorization' field of the request header (1004)
              http_code: '401'
            request_id: 021785229015510a2c883cf675b9804d
    Err402:
      description: Insufficient balance/quota
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/OaiError'
          example:
            type: error
            error:
              type: insufficient_balance_error
              message: insufficient balance (1008)
              http_code: '402'
            request_id: 021785229015510a2c883cf675b9804d
    Err422:
      description: Input contains sensitive content
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/OaiError'
          example:
            type: error
            error:
              type: unprocessable_entity_error
              message: video description contains sensitive content (1026)
              http_code: '422'
            request_id: 021785229015510a2c883cf675b9804d
    Err429:
      description: Rate limit triggered
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/OaiError'
          example:
            type: error
            error:
              type: rate_limit_error
              message: rate limit, please retry later (1002)
              http_code: '429'
            request_id: 021785229015510a2c883cf675b9804d
    Err500:
      description: Server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/OaiError'
          example:
            type: error
            error:
              type: server_error
              message: internal error (1000)
              http_code: '500'
            request_id: 021785229015510a2c883cf675b9804d
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: >-
        `HTTP: Bearer Auth`

        - Security Scheme Type: http

        - HTTP Authorization Scheme: `Bearer API_key`, used to verify account
        information, can be found in [Account Management>API
        Keys](https://platform.minimax.io/user-center/basic-information/interface-key).

````