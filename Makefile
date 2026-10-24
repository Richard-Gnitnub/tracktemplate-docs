# Adapted from the existing Companion/Railworks Sphinx scaffold.
# See NOTICE.md for source revisions and LICENSE for the retained MIT notice.
SPHINXOPTS    ?= -n -W --keep-going
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs
BUILDDIR      = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
