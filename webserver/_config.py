import json
import os


def prepare_swagger_json():
    # Create a static folder to store the Swagger JSON file
    if not os.path.exists("static"):
        os.makedirs("static")
    swagger_json = {
        "openapi": "3.0.0",
        "info": {
            "title": "Lightweight Webserver API",
            "version": "1.0.0"
        },
        "paths": {
            "/tasks": {
                "post": {
                    "summary": "Create a new scheduled task",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {
                                            "type": "string"
                                        },
                                        "interval": {
                                            "type": "integer"
                                        }
                                    },
                                    "required": [
                                        "task_id",
                                        "interval"
                                    ]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Task created successfully"
                        },
                        "400": {
                            "description": "Invalid input"
                        }
                    }
                },
                "get": {
                    "summary": "List all scheduled tasks",
                    "responses": {
                        "200": {
                            "description": "A list of scheduled tasks"
                        }
                    }
                }
            },
            "/tasks/{task_id}": {
                "delete": {
                    "summary": "Delete a scheduled task",
                    "parameters": [
                        {
                            "name": "task_id",
                            "in": "path",
                            "description": "Task ID",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Task deleted successfully"
                        },
                        "400": {
                            "description": "Invalid input"
                        }
                    }
                }
            },
            "/commands": {
                "get": {
                    "summary": "List all commands with pagination support",
                    "parameters": [
                        {
                            "name": "offset",
                            "in": "query",
                            "description": "Pagination offset",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 0
                            }
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Pagination limit",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "default": 10
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A list of commands"
                        }
                    }
                },
                "post": {
                    "summary": "Run a command",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {
                                            "type": "string"
                                        },
                                        "cwd": {
                                            "type": "string"
                                        },
                                        "timeout": {
                                            "type": "integer"
                                        }
                                    },
                                    "required": [
                                        "command"
                                    ]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Command submitted successfully"
                        }
                    }
                }
            },
            "/commands/{command_id}": {
                "get": {
                    "summary": "Get command status",
                    "parameters": [
                        {
                            "name": "command_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Command status retrieved successfully"
                        }
                    }
                }
            }
        }
    }

    with open("static/swagger.json", "w") as f:
        json.dump(swagger_json, f)
