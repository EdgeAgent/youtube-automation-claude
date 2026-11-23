"""YouTube Automation for Muse — pipeline package.

A niche-agnostic, human-in-the-loop pipeline:

    select  -> pick only moments that match proven winning types
    seo     -> build the full title / description / tags pack
    thumbnail -> build a thumbnail from a REAL frame of your own video
    qc      -> refuse to pass anything that fails the pre-publish gate

Uploading itself is a manual/assisted step in YouTube Studio (see README).
Nothing in this package uploads, posts, or calls the YouTube API.
"""

__all__ = ["config", "select", "seo", "thumbnail", "qc"]
__version__ = "0.1.0"
