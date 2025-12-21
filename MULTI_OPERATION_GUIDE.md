# Multi-Operation Mode Guide

The OpenAPI Generator tool supports generating a single OpenAPI specification file with multiple operations (GET, POST, PUT, PATCH, DELETE).

## Overview

When you have multiple API operations that should be documented together, you can use the **multi-operation mode** with a configuration file instead of generating separate OpenAPI files for each operation.

## Configuration File Format

The configuration file can be in **JSON** or **YAML** format. It should contain an `operations` array where each operation is defined.

### Required Fields for Each Operation

- `method`: HTTP method (GET, POST, PUT, PATCH, DELETE)
- `path`: API path (e.g., `/pet/{petId}`)
- `operation_id`: Unique operation identifier (e.g., `getPetById`)
- `response_json`: Path to the response JSON file

### Optional Fields for Each Operation

- `request_json`: Path to request JSON file (required for POST, PUT, PATCH, DELETE)
- `summary`: Operation summary
- `description`: Operation description
- `tags`: List of tags (array or single string)

### Optional Top-Level Fields

- `title`: API title (can also be provided via CLI `--title`)
- `version`: API version (can also be provided via CLI `--version`)
- `description`: API description (can also be provided via CLI `--api-description`)

## Example: YAML Configuration

```yaml
title: "Pet Store API"
version: "1.0.0"
description: "A comprehensive Pet Store API"

operations:
  # GET operation - Find pets by status
  - method: GET
    path: /pet/findByStatus
    operation_id: findPetsByStatus
    response_json: examples/get_response.json
    summary: "Finds Pets by status"
    description: "Multiple status values can be provided with comma separated strings"
    tags:
      - pet

  # GET operation - Get pet by ID
  - method: GET
    path: /pet/{petId}
    operation_id: getPetById
    response_json: examples/get_response.json
    summary: "Find pet by ID"
    description: "Returns a single pet"
    tags:
      - pet

  # POST operation - Add a new pet
  - method: POST
    path: /pet
    operation_id: addPet
    request_json: examples/post_request.json
    response_json: examples/post_response.json
    summary: "Add a new pet to the store"
    description: "Add a new pet to the store"
    tags:
      - pet

  # PUT operation - Update an existing pet
  - method: PUT
    path: /pet
    operation_id: updatePet
    request_json: examples/put_request.json
    response_json: examples/put_response.json
    summary: "Update an existing pet"
    description: "Update an existing pet by Id"
    tags:
      - pet

  # DELETE operation - Delete a pet
  - method: DELETE
    path: /pet/{petId}
    operation_id: deletePet
    request_json: examples/post_request.json
    response_json: examples/post_response.json
    summary: "Deletes a pet"
    description: "Delete a pet"
    tags:
      - pet
```

## Example: JSON Configuration

```json
{
  "title": "Pet Store API",
  "version": "1.0.0",
  "description": "A comprehensive Pet Store API",
  "operations": [
    {
      "method": "GET",
      "path": "/pet/findByStatus",
      "operation_id": "findPetsByStatus",
      "response_json": "examples/get_response.json",
      "summary": "Finds Pets by status",
      "description": "Multiple status values can be provided with comma separated strings",
      "tags": ["pet"]
    },
    {
      "method": "POST",
      "path": "/pet",
      "operation_id": "addPet",
      "request_json": "examples/post_request.json",
      "response_json": "examples/post_response.json",
      "summary": "Add a new pet to the store",
      "tags": ["pet"]
    }
  ]
}
```

## Usage

### Basic Usage

```bash
openapi-gen --config config.yaml --output openapi.yaml
```

### Custom Output Path

You can specify any output path, including nested directories. The tool will automatically create directories if they don't exist:

```bash
# Save to a subdirectory
openapi-gen --config config.yaml --output ./specs/api/openapi.yaml

# Save to nested directory structure
openapi-gen --config config.yaml --output ./output/v1/petstore/openapi.yaml

# Absolute path (Linux/Mac)
openapi-gen --config config.yaml --output /home/user/api-specs/petstore.yaml

# Absolute path (Windows)
openapi-gen --config config.yaml --output C:\Users\YourName\Documents\api-specs\petstore.yaml
```

### With API Metadata

```bash
openapi-gen \
  --config config.yaml \
  --output ./output/petstore-api.yaml \
  --title "Pet Store API" \
  --version "1.0.12" \
  --api-description "This is a sample Pet Store Server" \
  --terms-of-service "https://swagger.io/terms/" \
  --contact-email "apiteam@swagger.io" \
  --license-name "Apache 2.0" \
  --license-url "https://www.apache.org/licenses/LICENSE-2.0.html" \
  --server-url "https://petstore31.swagger.io/api/v3"
```

## Benefits of Multi-Operation Mode

1. **Single File**: All operations in one OpenAPI specification
2. **Shared Schemas**: Common schemas are defined once in `components/schemas`
3. **Consistent Metadata**: Same API title, version, and description for all operations
4. **Easier Management**: One config file to manage instead of multiple command-line calls
5. **Better Organization**: All related operations grouped together

## Path Parameters

Path parameters are automatically extracted from paths. For example:
- `/pet/{petId}` → automatically adds `petId` as a path parameter
- `/users/{userId}/posts/{postId}` → automatically adds both `userId` and `postId` as path parameters

## Schema Naming

Schemas are automatically named based on the `operation_id`:
- `getPetById` → `GetPetByIdRequest` and `GetPetByIdResponse`
- `addPet` → `AddPetRequest` and `AddPetResponse`

All schemas are stored in `components/schemas` and referenced using `$ref`.

## Tips

1. **Use relative paths** for JSON files in the config (relative to the config file location)
2. **Group related operations** using tags
3. **Reuse JSON files** for similar request/response structures
4. **Keep config files organized** - one config file per API or API version

## Comparison: Single vs Multi-Operation Mode

| Feature | Single Operation Mode | Multi-Operation Mode |
|---------|----------------------|---------------------|
| Operations per file | 1 | Multiple |
| Config file | Not needed | Required |
| Command complexity | Simple | Simple (uses config) |
| Best for | Quick single operations | Complete API documentation |
| Schema sharing | No | Yes (automatic) |

## Examples

See `examples/multi_operation_config.yaml` and `examples/multi_operation_config.json` for complete working examples.

