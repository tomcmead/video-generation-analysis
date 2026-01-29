import argparse
import time
from pathlib import Path

from video_generation_analysis.config import DATABASE_PATH
from video_generation_analysis.database_handler.database_handler import DatabaseHandler
from video_generation_analysis.database_handler.schema import VideoEngagementRecord
from video_generation_analysis.video_analytics.video_analytics import VideoAnalytics
from video_generation_analysis.video_generator.description_generator import (
    DescriptionGenerator,
)
from video_generation_analysis.video_generator.keyword_gensim_strategy import (
    KeywordGensimStrategy,
)
from video_generation_analysis.video_generator.keyword_huggingface_strategy import (
    KeywordHuggingFaceStrategy,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Video Generation, Publishing & Analysis Tool"
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        nargs="?",
        default="",
        help="Optional prompt to guide inital video generation."
        "Otherwise top keywords from database will be used.",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    db_handler = DatabaseHandler(Path(DATABASE_PATH), VideoEngagementRecord)
    description_generator = DescriptionGenerator(
        db_handler=db_handler,
        keyword_strategy=KeywordGensimStrategy(),
        description_strategy=KeywordHuggingFaceStrategy(),
    )
    video_analytics = VideoAnalytics(
        db_handler=db_handler, description_generator=description_generator
    )

    # generate inital video if prompt provided
    if args.prompt:
        video_analytics.generate_video(num_top_videos=10, prompt=args.prompt)

    # periodically generate new videos and update engagement metrics
    while True:
        video_analytics.generate_video(num_top_videos=10)
        video_analytics.update_video_metrics()
        time.sleep(86400)  # run once a day


if __name__ == "__main__":
    main()
