"""Helpers for validating and reading Hunter API JSON responses."""

from hunter_sdk.exceptions import HunterTransportError
from hunter_sdk.models import JsonObject


def ensure_json_object(payload: object) -> JsonObject:
    """Return a decoded JSON object or fail with a transport-level error."""
    if not isinstance(payload, dict):
        raise HunterTransportError("Hunter returned a JSON response that is not an object")

    fields_are_json = all(
        isinstance(field_name, str) and _is_json_value(field_value)
        for field_name, field_value in payload.items()
    )
    if fields_are_json:
        return payload
    raise HunterTransportError("Hunter returned a JSON response that is not an object")


def _is_json_value(payload: object) -> bool:
    """Check whether a value can be represented as JSON."""
    if payload is None or isinstance(payload, (str, int, float, bool)):
        return True
    if isinstance(payload, list):
        return all(_is_json_value(field_value) for field_value in payload)
    if isinstance(payload, dict):
        return all(
            isinstance(field_name, str) and _is_json_value(field_value)
            for field_name, field_value in payload.items()
        )
    return False


def read_object(payload: JsonObject, field_name: str, required: bool) -> JsonObject:
    """Read a JSON object field from a response payload."""
    field_value = payload.get(field_name)
    if field_value is None and not required:
        return {}
    try:
        return ensure_json_object(field_value)
    except HunterTransportError as invalid_object:
        message = "Hunter returned invalid `{0}` object".format(field_name)
        raise HunterTransportError(message) from invalid_object


def read_str(payload: JsonObject, field_name: str, required: bool) -> str | None:
    """Read a string field from a response payload."""
    field_value = payload.get(field_name)
    if field_value is None and not required:
        return None
    if isinstance(field_value, str):
        return field_value
    message = "Hunter returned invalid `{0}` string".format(field_name)
    raise HunterTransportError(message)


def read_optional_int(payload: JsonObject, field_name: str) -> int | None:
    """Read an optional integer field from a response payload."""
    field_value = payload.get(field_name)
    if field_value is None:
        return None
    if isinstance(field_value, int) and not isinstance(field_value, bool):
        return field_value
    message = "Hunter returned invalid `{0}` integer".format(field_name)
    raise HunterTransportError(message)


def read_object_list(payload: JsonObject, field_name: str) -> list[JsonObject]:
    """Read an optional list of JSON objects from a response payload."""
    field_value = payload.get(field_name)
    if field_value is None:
        return []
    if not isinstance(field_value, list):
        message = "Hunter returned invalid `{0}` array".format(field_name)
        raise HunterTransportError(message)

    object_items: list[JsonObject] = []
    for field_item in field_value:
        try:
            object_items.append(ensure_json_object(field_item))
        except HunterTransportError as invalid_item:
            message = "Hunter returned invalid `{0}` array".format(field_name)
            raise HunterTransportError(message) from invalid_item
    return object_items
