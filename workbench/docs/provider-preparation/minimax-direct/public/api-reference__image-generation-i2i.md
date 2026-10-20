> ## Documentation Index
> Fetch the complete documentation index at: https://platform.minimax.io/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Image-to-Image Generation

> Use this API to generate images from image input.



## OpenAPI

````yaml api-reference/image/generation/api/image-to-image.json POST /v1/image_generation
openapi: 3.1.0
info:
  title: MiniMax Image Generation API
  description: MiniMax image generation API for creating images from text prompts
  license:
    name: MIT
  version: 1.0.0
servers:
  - url: https://api.minimax.io
security:
  - bearerAuth: []
paths:
  /v1/image_generation:
    post:
      tags:
        - Image
      summary: Image Generation
      operationId: imageGeneration
      parameters:
        - name: Content-Type
          in: header
          required: true
          description: >-
            The media type of the request body. Must be set to
            `application/json` to ensure the data is sent in JSON format.
          schema:
            type: string
            enum:
              - application/json
            default: application/json
      requestBody:
        description: ''
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ImageGenerationReq'
        required: true
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ImageGenerationResp'
components:
  schemas:
    ImageGenerationReq:
      type: object
      required:
        - prompt
        - model
      properties:
        model:
          type: string
          description: 'Model name. Options: `image-01`.'
          enum:
            - image-01
            - image-01-live
        prompt:
          type: string
          description: Text description of the image, max length 1500 characters.
        subject_reference:
          type: array
          items:
            $ref: '#/components/schemas/ImageSubjectReference'
          description: Subject reference for image-to-image generation.
        aspect_ratio:
          type: string
          description: |-
            Image aspect ratio, default `1:1`. Options:
            - `1:1` (1024x1024)
            - `16:9` (1280x720)
            - `4:3` (1152x864)
            - `3:2` (1248x832)
            - `2:3` (832x1248)
            - `3:4` (864x1152)
            - `9:16` (720x1280)
            - `21:9` (1344x576)
          enum:
            - '1:1'
            - '16:9'
            - '4:3'
            - '3:2'
            - '2:3'
            - '3:4'
            - '9:16'
            - '21:9'
        width:
          type: integer
          description: >-
            Image width (px). Only effective for `image-01`. Must be set
            together with `height`. Range [512, 2048], must be divisible by 8.
            If both `width/height` and `aspect_ratio` are provided,
            `aspect_ratio` takes priority.
        height:
          type: integer
          description: >-
            Height of generated image (pixels). Only effective when `model` is
            `image-01`.

            Same rules as `width`.
        response_format:
          type: string
          enum:
            - url
            - base64
          default: url
          description: |-
            Response format for images. Default: url. Options: url, base64.
            ⚠️ Note: url expires in 24 hours.
        seed:
          type: integer
          format: int64
          description: >-
            Random seed. Using the same seed and parameters allows result
            reproduction.

            If omitted, each of the n images will use a unique random seed.
        'n':
          type: integer
          default: 1
          minimum: 1
          maximum: 9
          description: 'Number of images to generate per request. Range [1, 9]. Default: 1.'
        prompt_optimizer:
          type: boolean
          default: false
          description: 'Enable automatic optimization of prompt. Default: `false`.'
      example:
        model: image-01
        prompt: A girl looking into the distance from a library window
        aspect_ratio: '16:9'
        subject_reference:
          - type: character
            image_file: >-
              https://cdn.hailuoai.com/prod/2025-08-12-17/video_cover/1754990600020238321-411603868533342214-cover.jpg
        'n': 2
    ImageGenerationResp:
      type: object
      properties:
        data:
          $ref: '#/components/schemas/DataObject'
        metadata:
          type: object
          properties:
            success_count:
              type: integer
              description: Number of successfully generated images.
            failed_count:
              type: integer
              description: Number of images blocked due to content safety.
          description: Additional metadata about the generation.
        id:
          type: string
          description: Trace ID for request tracking
        base_resp:
          $ref: '#/components/schemas/BaseResp'
      example:
        id: 03ff3cd0820949eb8a410056b5f21d38
        data:
          image_urls:
            - XXX
            - XXX
            - XXX
        metadata:
          failed_count: '0'
          success_count: '3'
        base_resp:
          status_code: 0
          status_msg: success
    ImageSubjectReference:
      type: object
      required:
        - type
        - image_file
      properties:
        type:
          type: string
          description: Subject type. Currently only supports `character` (portrait).
        image_file:
          type: string
          description: "Reference image file. Supports public URLs or Base64-encoded [Data URL](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data) (`data:image/jpeg;base64,...`).\nFor best results, upload a single front-facing portrait photo.\n- Image requirements:\n\t- Formats: JPG, JPEG, PNG\n\t- Size: less than 10MB"
    DataObject:
      type: object
      properties:
        image_urls:
          type: array
          items:
            type: string
          description: >-
            Returned when `response_format` = `url`, contains an array of image
            links.
        image_base64:
          type: array
          items:
            type: string
          description: >-
            Returned when `response_format` = `base64`, contains an array of
            base64-encoded images.
    BaseResp:
      type: object
      properties:
        status_code:
          type: integer
          description: >-
            The status codes and their meanings are as follows:

            - `0`, Request successful

            - `1002`, Rate limit triggered, please try again later

            - `1004`, Account authentication failed, please check if the API Key
            is correct

            - `1008`, Insufficient account balance

            - `1026`, Sensitive content detected in prompt

            - `2013`, Invalid input parameters, please check if the parameters
            are filled in as required

            - `2049`, Invalid API Key


            For more information, please refer to the [Error Code
            Reference](/api-reference/errorcode).  
        status_msg:
          type: string
          description: Status details.
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: >-
        `HTTP: Bearer Auth`

        - Security Scheme Type: http

        - HTTP Authorization Scheme: `Bearer API_key`, can be found in [Account
        Management>API
        Keys](https://platform.minimax.io/user-center/basic-information/interface-key).

````