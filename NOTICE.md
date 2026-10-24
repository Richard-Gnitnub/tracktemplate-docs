# Sources and notices

## Existing Sphinx scaffold

The Makefile adapts the Sphinx build arrangement in:

- [Richard-Gnitnub/Railworks-Documentation](https://github.com/Richard-Gnitnub/Railworks-Documentation/tree/01295177743201cb24bc4fe2fc859a1b5cb749d6),
  revision `01295177743201cb24bc4fe2fc859a1b5cb749d6`.
- [ValleysEnduro/templot5companion](https://github.com/ValleysEnduro/templot5companion/tree/17f9fc4770379e9add7fb8bcaf3b2b0161e61d9a),
  revision `17f9fc4770379e9add7fb8bcaf3b2b0161e61d9a`.

The two source Makefiles contain the same build scaffold. This draft changes
the source directory to `docs/`, the output directory to `_build/` and the
default build options.

The original MIT licence, including
`Copyright (c) 2024 Rich Bunting`, is preserved verbatim in [LICENSE](LICENSE).

## New documentation

The TrackTemplate-facing pages, theme configuration and validation workflow
form the initial developer documentation for TrackTemplate contributors. They
do not speak on behalf of Martin Wynne or the Templot project.

The pages link to TrackTemplate's canonical source documents at revision
`54c5903b41e89d1fdfb430c812495e36b91d690b`. Those linked documents retain
their own licences, notices and authority. A link does not change those terms.

## Third-party build tools

Sphinx, MyST Parser, PyData Sphinx Theme and the GitHub Actions used by this
scaffold retain their respective upstream licences. The requirements file
identifies the direct Python dependencies. Action revisions are pinned in the
validation workflow.
