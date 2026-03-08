from typing import ClassVar, Type, Generic, TypeVar
from pydantic import BaseModel, Field
from i2psam.utils import format_kw, tokenize_sam_line, parse_kw_tokens
from i2psam.exceptions import SAMError
from i2psam.types import Result


class I2PMessage(BaseModel):
    command: ClassVar[str]
    subcommand: ClassVar[str | None] = None

    def get_kw(self):
        kw = []
        for k, v in self.__class__.model_fields.items():
            field_name = v.alias or k
            field_value = getattr(self, k)
            if field_value is None:
                continue
            kw.append(format_kw(field_name, field_value))
        return kw

    def _enshure_terminated(self, line: str):
        if not line.endswith("\n"):
            return line + "\n"
        return line

    def to_message(self) -> str:
        if not self.command:
            raise ValueError("At least command must be defined")
        parts = (
            [self.command, self.subcommand]
            if self.subcommand is not None
            else [self.command]
        )
        parts += self.get_kw()
        line = " ".join(parts)
        return self._enshure_terminated(line)

    def to_bytes(self) -> bytes:
        return self.to_message().encode("utf-8")

    def __str__(self):
        return self.to_message()

    @classmethod
    def parse(cls, line: str | bytes):
        if isinstance(line, bytes):
            line = str(line.decode("utf-8"))

        if line.endswith("\n"):
            line = line[:-1]

        cls.raw = line
        tokens = tokenize_sam_line(line)
        cmd = tokens[0]
        sub = tokens[1] if cls.subcommand is not None else None
        opts = parse_kw_tokens(tokens[(2 if sub is not None else 1) :])

        try:
            obj = cls.model_validate(opts)
        except Exception as e:
            raise SAMError(
                f"Could not parse reply {line!r} as {cls.__name__}: {e}"
            ) from e

        if cls.command and cmd.upper() != cls.command.upper():
            raise SAMError(
                f"Unexpected reply command {cmd!r}, expected {cls.command!r}: {line!r}"
            )
        if sub and cls.subcommand and sub.upper() != cls.subcommand.upper():
            raise SAMError(
                f"Unexpected reply subcommand {sub!r}, expected {cls.subcommand!r}: {line!r}"
            )
        return obj


R = TypeVar("R", bound="I2PReply")


class I2PReply(I2PMessage):
    result: Result | None = Field(alias="RESULT", default=None)
    message: str | None = Field(alias="MESSAGE", default=None)

    @property
    def is_ok(self):
        if self.result is not None:
            return self.result == Result.OK
        return True


class I2PCommand(I2PMessage, Generic[R]):
    response_class: ClassVar[Type[R]]

    @classmethod
    def parse_response(cls, msg: str | bytes) -> R:
        if cls.response_class:
            return cls.response_class.parse(msg)
        return None
