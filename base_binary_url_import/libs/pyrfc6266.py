import re
import uuid
from dataclasses import dataclass
from typing import List, Tuple
from urllib.parse import unquote, urlparse

from .pyparsing import (
    CaselessLiteral,
    Combine,
    Empty,
    Literal,
    OneOrMore,
    Optional,
    ParseException,
    QuotedString,
    Regex,
    Word,
    ZeroOrMore,
    alphas,
)

__all__ = [
    "parse",
    "parse_filename",
    "secure_filename",
    "requests_response_to_filename",
    "ContentDisposition",
]


@dataclass
class ContentDisposition:
    name: str
    value: str


token_chars = (
    "!#$%&'*+-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz|~"
)
token_chars_without_wildcard = (
    "!#$%&'+-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz|~"
)
token = Word(token_chars)
unencoded_token = Regex(
    r"[%s]*[%s]" % (re.escape(token_chars), re.escape(token_chars_without_wildcard))
)
value = token | QuotedString(
    quote_char='"', esc_quote='\\"', esc_char="\\", convert_whitespace_escapes=False
)  # TODO: make sure it does not parse invalid <any OCTET except CTLs, but including LWS>
ext_value = Combine(
    (
        CaselessLiteral("UTF-8") | CaselessLiteral("ISO-8859-1") | Empty()
    ).set_results_name("encoding")
    + Literal("'")
    + Optional(Word(alphas + " ", min=1, max=3)).set_results_name("language")
    + Literal("'")
    + OneOrMore(
        Word(
            "!#$&+-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz|~"
        )
        | (Literal("%") + Word("abcdefABCDEF0123456789", exact=2))
    ).set_results_name("value")
)
disp_ext_parm = (
    (unencoded_token + Literal("=")).set_results_name("parm*")
    + value.set_results_name("value*")
) | (
    (Combine(unencoded_token + Literal("*")) + Literal("=")).set_results_name("parm*")
    + value.set_results_name("value*")
)

# filename_parm = (Combine(Literal("filename").set_results_name("parm*") + Literal('=')) + value) | (Literal("filename*=") + ext_value)
disp_ext_type = token
# disposition_parm = filename_parm | disp_ext_parm
disposition_parm = disp_ext_parm
disposition_type = (
    CaselessLiteral("inline") | CaselessLiteral("attachment") | disp_ext_type
)

parser = (
    disposition_type.set_results_name("type")
    + ZeroOrMore(Literal(";") + disposition_parm)
    + Optional(";")
)

INVALID_ISO8859_1_CHARACTERS = set(
    bytes(list(range(0, 32)) + list(range(127, 160))).decode("iso-8859-1")
)


def parse(header: str) -> Tuple[str, List[ContentDisposition]]:
    """Parse a Content-Disposition header into its components.

    Args:
        header: The actual header value as string

    Returns:
        A tuple consisting of content disposition type and a list
        of found dispositions.
    """
    parse_result = parser.parse_string(header, parse_all=True)

    content_disposition_type = parse_result["type"].lower()
    all_content_disposition = []
    seen_parms = set()
    for parm, value in zip(parse_result.get("parm", []), parse_result.get("value", [])):
        parm = "".join(parm)
        if parm in seen_parms:
            raise ParseException(f"Multiple parms with same name found: {parm}")
        seen_parms.add(parm)
        parm = parm[:-1].lower()
        if parm.endswith("*"):
            parse_result_value = ext_value.parse_string(value, parse_all=True)
            if "encoding" not in parse_result_value:
                continue
            encoding = parse_result_value["encoding"].lower()
            try:
                value = unquote(
                    "".join(parse_result_value["value"]),
                    encoding=encoding,
                    errors="strict",
                )
            except UnicodeDecodeError:
                raise ParseException("Invalid encoding found")
            if encoding == "iso-8859-1":
                if (
                    set(value) & INVALID_ISO8859_1_CHARACTERS
                ):  # Python should really do this by itself
                    raise ParseException("Invalid encoding found")
        all_content_disposition.append(ContentDisposition(parm, value))

    return content_disposition_type, all_content_disposition


def secure_filename(filename: str) -> str:
    """Rudimentary security for filenames.

    Args:
        filename: A potentially insecure filename.

    Returns:
        A likely secure filename.
    """
    return filename.replace("\\", "_").replace("/", "_")


def parse_filename(header: str, enforce_content_disposition_type: bool = False) -> str:
    """Returns a safe filename from a content-disposition header

    Args:
        header: The actual header value as string
        enforce_content_disposition_type: Enforce content-disposition type to one of the two known types.

    Returns:
        None if no filename could be found
        str if a filename could be found
    """
    content_disposition_type, all_content_disposition = parse(header)
    allowed_content_dispositions = ["attachment", "inline"]
    if (
        enforce_content_disposition_type
        and content_disposition_type not in allowed_content_dispositions
    ):
        return None

    def normal_filename(content_disposition):
        return content_disposition.value

    def combine_filename(content_disposition):
        filename = content_disposition.value
        for i in range(1, 99999):
            found_value = False
            for name in [f"filename*{i}*", f"filename*{i}"]:
                for content_disposition in all_content_disposition:
                    if content_disposition.name == name:
                        filename += content_disposition.value
                        found_value = True
                        break
                if found_value:
                    break
            else:
                break
        return filename

    header_handlers = [
        ("filename*", normal_filename),
        ("filename", normal_filename),
        ("filename*0*", combine_filename),
        ("filename*0", combine_filename),
    ]

    filename = None
    for name, handler_func in header_handlers:
        for content_disposition in all_content_disposition:
            if content_disposition.name == name:
                filename = handler_func(content_disposition)
                if filename:
                    break
        if filename:
            break

    if filename:
        filename = secure_filename(filename)
    return filename


def requests_response_to_filename(
    response, enforce_content_disposition_type: bool = False
) -> str:
    """Turn a requests response into a filename

    Args:
        response: `requests.Response`
        enforce_content_disposition_type: Enforce content-disposition type to one of the two known types.

    Returns:
        a filename as a string.
    """
    content_disposition = response.headers.get("Content-Disposition")
    filename = None
    if content_disposition:
        filename = parse_filename(
            content_disposition,
            enforce_content_disposition_type=enforce_content_disposition_type,
        )

    if not filename:
        url = urlparse(response.url)
        url_path = url.path.lstrip("/")
        if url_path:
            url_path = url_path.split("/")[-1]
            if url_path:
                filename = secure_filename(url_path)

    if not filename:
        filename = f"unknown-{uuid.uuid4()}"

    return filename
