# Headers Support Guide

The OpenAPI Generator tool automatically includes common request and response headers that organizations typically require for API operations.

## Default Headers

### Request Headers (in `parameters`)

The tool automatically includes the following request headers by default:

1. **Authorization** - Bearer token for authentication
2. **X-Request-ID** - Unique identifier for the request (UUID format)
3. **X-Correlation-ID** - Correlation ID for tracking requests across services (UUID format)
4. **X-Request-Date** - Request timestamp (date-time format)
5. **X-Client-ID** - Client identifier
6. **Content-Type** - Content type of the request body (application/json, application/xml, application/x-www-form-urlencoded)
7. **Accept** - Accepted response content types (application/json, application/xml)

### Response Headers (in `responses`)

The tool automatically includes the following response headers in all responses:

1. **X-Request-ID** - Echo of the request ID
2. **X-Correlation-ID** - Echo of the correlation ID
3. **X-Response-Time** - Response processing time in milliseconds
4. **X-Rate-Limit-Remaining** - Number of requests remaining in the current rate limit window
5. **X-Rate-Limit-Reset** - Time when the rate limit window resets

## Usage

### Single Operation Mode

Headers are included by default:

```bash
openapi-gen \
  --method GET \
  --path /users/{id} \
  --response-json response.json \
  --operation-id getUserById
```

To disable default headers:

```bash
openapi-gen \
  --method GET \
  --path /users/{id} \
  --response-json response.json \
  --operation-id getUserById \
  --no-default-headers
```

### Multi-Operation Mode

Headers are included by default for all operations. You can control this per operation in the config file:

```yaml
operations:
  - method: GET
    path: /users/{id}
    operation_id: getUserById
    response_json: examples/get_response.json
    include_default_headers: true  # Default: true
    
  - method: POST
    path: /users
    operation_id: createUser
    request_json: examples/post_request.json
    response_json: examples/post_response.json
    include_default_headers: false  # Disable for this operation
```

## Custom Headers

### In Config File (Multi-Operation Mode)

You can add custom headers per operation:

```yaml
operations:
  - method: GET
    path: /users/{id}
    operation_id: getUserById
    response_json: examples/get_response.json
    request_headers:
      - name: X-Custom-Header
        in: header
        description: Custom header description
        required: false
        schema:
          type: string
          example: "custom-value"
    response_headers:
      X-Custom-Response-Header:
        description: Custom response header
        schema:
          type: string
```

### Request Headers Format

```yaml
request_headers:
  - name: Header-Name
    in: header
    description: Header description
    required: true  # or false
    schema:
      type: string  # or integer, boolean, etc.
      format: uuid  # optional
      example: "example-value"  # optional
      enum: ["value1", "value2"]  # optional
```

### Response Headers Format

```yaml
response_headers:
  Header-Name:
    description: Header description
    schema:
      type: string
      format: uuid
      example: "example-value"
```

## Example Generated OpenAPI Spec

```yaml
paths:
  /users/{id}:
    get:
      operationId: getUserById
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
        - name: Authorization
          in: header
          description: Bearer token for authentication
          required: false
          schema:
            type: string
            example: "Bearer <token>"
        - name: X-Request-ID
          in: header
          description: Unique identifier for the request
          required: false
          schema:
            type: string
            format: uuid
        # ... more headers
      responses:
        '200':
          description: Successful operation
          headers:
            X-Request-ID:
              description: Echo of the request ID
              schema:
                type: string
                format: uuid
            # ... more headers
```

## Benefits

1. **Enterprise-Ready**: Includes headers commonly required by enterprise APIs
2. **Consistent**: Same headers across all operations
3. **Customizable**: Can add custom headers or disable defaults
4. **Standards-Compliant**: Follows OpenAPI 3.1.0 specification
5. **Documentation**: Headers are properly documented with descriptions and examples

## Common Use Cases

- **Authentication**: Authorization header for bearer tokens
- **Request Tracking**: X-Request-ID and X-Correlation-ID for distributed tracing
- **Client Identification**: X-Client-ID for identifying clients
- **Rate Limiting**: X-Rate-Limit-* headers for rate limit information
- **Performance Monitoring**: X-Response-Time for performance metrics

## Notes

- All default headers are marked as `required: false` to allow flexibility
- Headers are included in all HTTP responses (200, 400, 404, etc.)
- Custom headers override default headers with the same name
- Headers follow OpenAPI 3.1.0 parameter and header specifications

