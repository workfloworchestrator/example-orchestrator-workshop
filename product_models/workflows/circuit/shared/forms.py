from pydantic import validator

from orchestrator.types import State

from surf.utils.exceptions import FieldValueError


def validate_something(foo: str | None, values: State) -> str | None:

    if foo:
        message = "TODO: implement this!"
        raise FieldValueError(message)

    return foo


def circuit_id_must_be_unique_validator() -> classmethod:
    return validator("circuit_id", allow_reuse=True)(validate_something)

