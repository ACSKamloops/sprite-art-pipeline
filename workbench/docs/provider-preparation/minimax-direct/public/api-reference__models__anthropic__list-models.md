> ## Documentation Index
> Fetch the complete documentation index at: https://platform.minimax.io/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# List Models

> Returns a list of all available models compatible with Anthropic API specification.



## OpenAPI

````yaml api-reference/models/anthropic/api/list-models.json GET /anthropic/v1/models
openapi: 3.1.0
info:
  title: MiniMax Models API
  description: MiniMax models API compatible with Anthropic API specification.
  version: 1.0.0
servers:
  - url: https://api.minimax.io
security:
  - apiKeyAuth: []
paths:
  /anthropic/v1/models:
    get:
      tags:
        - Models
      summary: List Models
      description: >-
        Returns a list of all available models. This endpoint is compatible with
        Anthropic API specification.
      operationId: anthropicListModels
      parameters:
        - name: limit
          in: query
          required: false
          description: Number of items to return per page
          schema:
            type: integer
        - name: after_id
          in: query
          required: false
          description: Pagination cursor, returns models after this ID
          schema:
            type: string
        - name: before_id
          in: query
          required: false
          description: Pagination cursor, returns models before this ID
          schema:
            type: string
      responses:
        '200':
          description: A list of available models.
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    description: Array of model objects
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          description: Model identifier
                        created_at:
                          type: string
                          description: Model creation time (ISO 8601 format)
                        display_name:
                          type: string
                          description: Model display name
                        type:
                          type: string
                          description: Model type, always "model"
                  first_id:
                    type: string
                    description: First model ID in the returned data
                  has_more:
                    type: boolean
                    description: Whether there is more data
                  last_id:
                    type: string
                    description: Last model ID in the returned data
              examples:
                Default:
                  value:
                    data:
                      - id: MiniMax-M3
                        created_at: '2026-06-01T00:00:00Z'
                        display_name: MiniMax-M3
                        type: model
                      - id: MiniMax-M2.7
                        created_at: '2026-03-18T02:00:00Z'
                        display_name: MiniMax-M2.7
                        type: model
                      - id: MiniMax-M2.5
                        created_at: '2026-02-13T02:00:00Z'
                        display_name: MiniMax-M2.5
                        type: model
                    first_id: MiniMax-M3
                    has_more: false
                    last_id: MiniMax-M2.5
components:
  securitySchemes:
    apiKeyAuth:
      type: apiKey
      in: header
      name: X-Api-Key
      description: |-
        `API Key Auth`
         - Security Scheme Type: apiKey
         - API Key Header: X-Api-Key, used for account verification, can be viewed in [Account Management > API Keys](https://platform.minimax.io/user-center/basic-information/interface-key)

````