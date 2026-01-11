from pathlib import Path

import pytest
from dotenv import load_dotenv

from video_generation_analysis.video_generator.video_generator import VideoGenerator


def test_video_generator_valid(monkeypatch):
    load_dotenv()
    monkeypatch.setenv("GEMINI_API_KEY", "TEST_API_KEY")

    vg = VideoGenerator()

    assert vg._gemini_api_key == "TEST_API_KEY"


def test_video_generator_invalid(monkeypatch):
    load_dotenv()
    monkeypatch.setenv("GEMINI_API_KEY", "")

    with pytest.raises(ValueError):
        VideoGenerator()

def test_delete_local_video():
    vg = VideoGenerator()
    temp_video_path = Path("test_video.mp4")
    temp_video_path.touch()
    assert temp_video_path.is_file()

    vg.delete_local_video(temp_video_path)

    assert not temp_video_path.is_file()
