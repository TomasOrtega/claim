import re
from urllib.parse import quote, unquote
from urllib.request import HTTPRedirectHandler, build_opener

from claim.limits import MAX_ARTIFACT_BYTES


def raw_url(url: str) -> str:
    match = re.fullmatch(
        r"https://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+)/blob/"
        r"([0-9a-f]{40})/([^\s?#]+)",
        url,
    )
    if match is None or len(url) > 4096:
        raise ValueError("proof URL must be a GitHub file link pinned to a full commit")
    owner, repo, commit, path = match.groups()
    parts = [unquote(part) for part in path.split("/")]
    if repo in {".", ".."} or any(
        part in {"", ".", ".."} or re.search(r"[/\\\x00-\x1f\x7f]", part)
        for part in parts
    ):
        raise ValueError("invalid proof URL path")
    path = "/".join(quote(part, safe="") for part in parts)
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{path}"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("proof URL must not redirect")


def fetch(url: str) -> bytes:
    with build_opener(NoRedirect()).open(raw_url(url), timeout=30) as response:
        proof = response.read(MAX_ARTIFACT_BYTES + 1)
    if len(proof) > MAX_ARTIFACT_BYTES:
        raise ValueError("proof exceeds size limit")
    return proof
