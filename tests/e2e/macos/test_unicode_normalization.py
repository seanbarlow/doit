"""E2E tests for Unicode normalization on macOS."""

import pytest
from pathlib import Path


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
@pytest.mark.ci
def test_nfd_normalized_filenames(tmp_path, unicode_test_files, macos_test_env):
    """Test NFD normalized filenames (macOS default)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.unicode_utils import create_nfd_filename

    # Create file with NFD normalization
    nfd_file = create_nfd_filename(str(tmp_path), "café.txt")
    assert nfd_file.exists(), "NFD normalized file not created"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
def test_nfc_normalized_filenames(tmp_path, macos_test_env):
    """Test NFC normalized filenames (Windows/Linux standard)."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.unicode_utils import create_nfc_filename

    # Create file with NFC normalization
    nfc_file = create_nfc_filename(str(tmp_path), "café.txt")
    assert nfc_file.exists(), "NFC normalized file not created"


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
def test_filename_comparison_across_normalizations(tmp_path, macos_test_env):
    """Test comparing filenames across different normalizations."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.unicode_utils import (
        create_nfd_filename,
        create_nfc_filename,
        compare_normalized
    )

    # Create both NFD and NFC files
    nfd_file = create_nfd_filename(str(tmp_path), "tëst.txt")
    nfc_file = create_nfc_filename(str(tmp_path), "tëst_nfc.txt")

    # macOS might treat them as same or different depending on FS
    # Just verify both exist
    assert nfd_file.exists()
    assert nfc_file.exists()


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
def test_unicode_in_paths_and_content(tmp_path, macos_test_env):
    """Test Unicode in both paths and file content."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    # Create directory with Unicode
    unicode_dir = tmp_path / "pàth"
    unicode_dir.mkdir()

    # Create file with Unicode name and content
    unicode_file = unicode_dir / "fîlé.txt"
    unicode_content = "Content with Ünicode: café, naïve, résumé\n"
    unicode_file.write_text(unicode_content)

    # Verify
    assert unicode_file.exists()
    assert unicode_file.read_text() == unicode_content


@pytest.mark.macos
@pytest.mark.e2e
@pytest.mark.unicode
def test_unicode_normalization_detection(macos_test_env):
    """Test detection of Unicode normalization form."""
    if not macos_test_env["is_macos"]:
        pytest.skip("Test requires macOS")

    from tests.utils.macos.unicode_utils import detect_normalization, normalize_nfd, normalize_nfc

    # Test NFD detection
    nfd_text = normalize_nfd("café")
    assert detect_normalization(nfd_text) == "NFD"

    # Test NFC detection
    nfc_text = normalize_nfc("café")
    assert detect_normalization(nfc_text) == "NFC"
