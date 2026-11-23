"""YouTube Automation for Muse — pipeline package.

A niche-agnostic, human-in-the-loop pipeline:

    select  -> pick only moments that match proven winning types
    produce -> cut, format, caption, and assemble the actual videos
               (ffmpeg, on footage the user supplies locally)
    seo     -> build the full title / description / tags pack
    thumbnail -> build a thumbnail from a REAL frame of your own video
    qc      -> refuse to pass anything that fails the pre-publish gate

Niche presets live in ``pipeline/niches.py`` over ``config/niches/``.

Uploading itself is a manual/assisted step in YouTube Studio (see README).
Nothing in this package uploads, posts, calls the YouTube API, or
downloads anyone's footage.
"""

__all__ = ["config", "niches", "select", "produce", "seo", "thumbnail", "qc"]
__version__ = "0.2.0"
