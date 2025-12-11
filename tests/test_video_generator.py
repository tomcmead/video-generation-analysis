import pytest
from dotenv import load_dotenv

from video_generation_analysis.video_generator.video_generator import VideoGenerator


def test_video_generator_valid(monkeypatch):
    load_dotenv()
    monkeypatch.setenv("GEMINI_API_KEY", "TEST_API_KEY")

    vb = VideoGenerator()

    assert vb._gemini_api_key == "TEST_API_KEY"


def test_video_generator_invalid(monkeypatch):
    load_dotenv()
    monkeypatch.setenv("GEMINI_API_KEY", "")

    with pytest.raises(ValueError):
        VideoGenerator()
