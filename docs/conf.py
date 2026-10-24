"""Documentation configuration. This build does not import TrackTemplate."""

project = "TrackTemplate"
author = "TrackTemplate contributors"
copyright = "2026, TrackTemplate contributors"
release = "development"

extensions = ["myst_parser"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
root_doc = "index"
language = "en"
exclude_patterns = ["Thumbs.db", ".DS_Store"]
smartquotes = False
nitpicky = True
myst_heading_anchors = 3

html_theme = "pydata_sphinx_theme"
html_title = "TrackTemplate developer documentation"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = True

html_theme_options = {
    "logo": {"text": "TrackTemplate"},
    "show_prev_next": True,
    "show_nav_level": 2,
    "navigation_depth": 2,
    "header_links_before_dropdown": 6,
    "icon_links": [
        {
            "name": "TrackTemplate source",
            "url": "https://github.com/Richard-Gnitnub/tracktemplate",
            "icon": "fa-brands fa-github",
        }
    ],
}
