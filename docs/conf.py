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
templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = True
html_sidebars = {"**": ["sidebar-collapse.html", "site-nav.html"]}

html_theme_options = {
    "logo": {"text": "TrackTemplate"},
    "show_prev_next": True,
    "show_nav_level": 1,
    "navigation_depth": 2,
    "collapse_navigation": False,
    # Use one site tree. Header page links otherwise repeat above it on mobile.
    "navbar_center": [],
    "icon_links": [
        {
            "name": "TrackTemplate source",
            "url": "https://github.com/Richard-Gnitnub/tracktemplate",
            "icon": "fa-brands fa-github",
        }
    ],
}


def _label_site_navigation(tree):
    """Name native branch controls without changing the theme's cached tree."""
    from bs4 import BeautifulSoup

    navigation = BeautifulSoup(str(tree), "html.parser")
    for item in navigation.select("li.has-children"):
        link = item.find("a", recursive=False)
        details = item.find("details", recursive=False)
        if link is None or details is None:
            continue
        summary = details.find("summary", recursive=False)
        if summary is not None:
            summary["aria-label"] = (
                f"Toggle {link.get_text(' ', strip=True)} navigation"
            )
    return str(navigation)


def _add_site_navigation_helper(app, pagename, templatename, context, doctree):
    context["label_site_navigation"] = _label_site_navigation


def setup(app):
    # Make the helper available before PyData checks sidebar templates.
    app.connect("html-page-context", _add_site_navigation_helper, priority=100)
