"""Instructional-video understanding agent boundary."""


class VideoInstructorAgent:
    """Understand demonstrations from supported URLs or uploaded videos.

    Not implemented. The responsibility is currently met directly by
    `GeminiService.extract_procedure`, which sends one approved YouTube URL to
    the compatibility model and returns a typed procedure. This class exists so
    the planned separation between understanding a demonstration and
    structuring it stays visible; it must not silently return a fabricated
    result.
    """

    def understand(self, source_url: str) -> None:
        """Raise until video understanding is a separate step."""
        raise NotImplementedError(
            "Video understanding is not implemented. Use GeminiService."
            f" Requested source: {source_url}"
        )
