"""Endpoint-level Tests for DOCX Upload Validation and Security Guards (Addition 2).
Enforces:
- Zip bomb rejection (400 Bad Request)
- Macro file rejection (.docm or vbaProject.bin) (400 Bad Request)
- Encrypted/password-protected file rejection (400 Bad Request)
- Wrong file type rejection (.pdf / .txt) (400 Bad Request)
- Oversized file rejection (> 5 MB) (400 Bad Request)
"""

import io
import zipfile
import pytest
from httpx import AsyncClient, ASGITransport
from docx import Document

from app.main import app
from app.api.deps import get_current_user, CurrentUser


def _create_minimal_docx_bytes() -> bytes:
    doc = Document()
    doc.add_heading("Alex Mercer", level=0)
    doc.add_paragraph("Full-Stack Engineer")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture
def mock_auth_user(monkeypatch):
    """Overrides get_current_user dependency so tests can focus strictly on endpoint validation."""
    test_user = CurrentUser(id="test_user_id_123", email="test@example.com")
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield test_user
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_endpoint_rejects_oversized_file(mock_auth_user):
    """File exceeding 5 MB must be rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create fake zip header + 5MB + 10 bytes
        fake_data = b"PK\x03\x04" + b"0" * (5 * 1024 * 1024 + 10)
        files = {"file": ("large.docx", fake_data, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        resp = await client.post("/api/templates/upload", files=files)
        assert resp.status_code == 400
        assert "exceeds maximum allowed size" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_endpoint_rejects_macro_extension(mock_auth_user):
    """Macro-enabled .docm extension must be rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        data = _create_minimal_docx_bytes()
        files = {"file": ("resume.docm", data, "application/vnd.ms-word.document.macroEnabled.12")}
        resp = await client.post("/api/templates/upload", files=files)
        assert resp.status_code == 400
        assert "Macro-enabled" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_endpoint_rejects_macro_binary_payload(mock_auth_user):
    """A .docx file containing vbaProject.bin must be rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("word/document.xml", "<document><body>test</body></document>")
            zf.writestr("word/vbaProject.bin", b"VBA_MALICIOUS_PAYLOAD")

        files = {"file": ("stealth_macro.docx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        resp = await client.post("/api/templates/upload", files=files)
        assert resp.status_code == 400
        assert "macro components" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_endpoint_rejects_wrong_type_pdf(mock_auth_user):
    """Sending a PDF to the DOCX templates endpoint must be rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("resume.pdf", b"%PDF-1.4 fake pdf bytes", "application/pdf")}
        resp = await client.post("/api/templates/upload", files=files)
        assert resp.status_code == 400
        assert "Only Microsoft Word (.docx)" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_endpoint_rejects_encrypted_file(mock_auth_user):
    """Encrypted/password-protected OLE document must be rejected with 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Standard OLE Compound File header for password protected office files
        ole_header = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 100
        files = {"file": ("protected.docx", ole_header, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        resp = await client.post("/api/templates/upload", files=files)
        assert resp.status_code == 400
        assert "password" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_endpoint_rejects_zip_bomb(mock_auth_user):
    """Zip archive with excessive entries (> 200) must trigger zip-bomb protection (400)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("word/document.xml", "<document><body>test</body></document>")
            for i in range(250):
                zf.writestr(f"word/part_{i}.xml", f"<p>content_{i}</p>")

        files = {"file": ("bomb.docx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        resp = await client.post("/api/templates/upload", files=files)
        assert resp.status_code == 400
        assert "Zip bomb protection" in resp.json()["detail"]
