import json
import logging
from typing import get_type_hints, Literal, Type, Union, TypeVar
from pydantic import BaseModel
from ollama import chat

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def model_to_class_string(model_cls: type[BaseModel]) -> str:
    """
    Converts a Pydantic model class to a string representing its class definition,
    with fields, types, and default None values.
    """
    lines = [f"class {model_cls.__name__}(BaseModel):"]
    type_hints = get_type_hints(model_cls)

    for field_name, field_type in type_hints.items():
        # Convert type to string
        type_str = getattr(field_type, '__name__', str(field_type))
        # Handle Optional / None types
        type_str = str(field_type).replace("typing.Optional[", "").replace("]", " | None")
        # Default all fields to None
        lines.append(f"    {field_name}: {type_str} = None")
    
    return "\n".join(lines)


async def call_ollama_chat(
    prompt: str,
    model: str = "qwen3:8b",
    think=False,
) -> str:
    """
    Helper function to call local Ollama model using OpenAI-compatible API.
    
    Args:
        prompt: The prompt to send the model
        model: Name of the Ollama model to use
    
    Returns:
        The model's response content as a string
    """
    try:
        messages=[
            {"role": "system", "content": "You are a helpful insurance claim assistant."},
            {"role": "user", "content": prompt}
        ]

        logger.info(f"Calling Ollama chat - model: {model}, think: {think}")
        logger.info(f"Prompt: {prompt[200:]}..." if len(prompt) > 200 else f"Prompt: {prompt}")

        response = chat(model, messages=messages, think=think)
        content = response.message.content

        if not content:
            raise Exception("No content returned from model")

        logger.info(f"Received response ({len(content)} chars)")
        logger.info(f"Response: {content}..." if len(content) > 200 else f"Response: {content}")

        return content
    
    except Exception as e:
        logger.error(f"Ollama chat failed: {str(e)}")
        raise e




async def call_ollama_structured(
    prompt: str,
    response_model: Type[T],
    model: str = "qwen3:8b",
    think=False,
) -> T:
    """
    Helper function to call local Ollama model with structured output using Pydantic models.
    
    Args:
        prompt: The prompt to send the model
        response_model: Pydantic model class defining the expected output structure
        model: Name of the Ollama model to use
    
    Returns:
        Instance of the response_model with parsed data
    """
    messages=[
        {"role": "system", "content": "You are a helpful travel insurance claim assistant. Always respond with valid JSON."},
        {"role": "user", "content": prompt}
    ]

    logger.info(f"Calling Ollama structured - model: {model}, response_model: {response_model.__name__}, think: {think}")
    logger.info(f"Prompt: {prompt}..." if len(prompt) > 200 else f"Prompt: {prompt}")

    try:
        response = chat(
            model=model,
            messages=messages,
            format=response_model.model_json_schema(),
            options={"temperature": 0},
            think=think,
        )
        
        content = response.message.content
        if not content:
            raise Exception("No content returned from model")

        logger.info(f"Raw response: {content}")

        json_data = json.loads(content)
        validated_response = response_model.model_validate(json_data)
        
        logger.info(f"Successfully parsed {response_model.__name__}")
        return validated_response
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Ollama structured call failed: {str(e)}")
        raise e

