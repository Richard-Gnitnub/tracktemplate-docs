# Code walkthroughs

Follow GUI workflows from their inputs through the code to their results.
These chapters explain design intent, calculations, state changes and failure
behaviour. Each chapter identifies the source revision and implementation
limits it covers.

Start with [Generate a template set](generate-template-set.md) for the main
generation and replacement workflow. The calculation and output chapters
explain its individual features. [Transition editing](transition-edit.md)
covers a separately activated editor for Euler (clothoid) transitions.
[C10 turnout placement and editing](turnout-placement-and-editing.md) follows
the switch-toe position through the host alignment, source geometry and
transactional changes to a managed turnout. [Crossover geometry and
preflight](crossover-geometry.md) then connects two mapped C10s and checks
the complete resulting radius before native construction.
[Turnout–crossover conversion](turnout-crossover-conversion.md) explains
how their identities and original output options survive a reversible
replacement, including the limits of older stored records.
[Crossover timbering](crossover-timbering.md) follows source supports through
conflict analysis, shared envelopes, controlled movement and reversible
automatic previews.
[Chair-position analysis](chair-analysis.md) follows a rail–timber support
through source assignment and an analytical footprint, then explains
current-input signatures, stale results and guarded reuse.
[Model timber support and 2D layout](chair-support-and-2d-layout.md) then
follows the rotated support envelope through bounded side extensions,
effective timber outlines, failed-fit overlays and display reuse.

```{toctree}
:maxdepth: 1

Generate a template set <generate-template-set>
Curves and spacing <curves-and-spacing>
Straight routes <straight-routes>
Physical platforms <platforms>
Formation boards <formation-board>
Universal sectioning <sectioning>
Assembly and fixing <assembly-and-fixing>
Transition editing <transition-edit>
C10 turnout placement and editing <turnout-placement-and-editing>
Crossover geometry and preflight <crossover-geometry>
Turnout–crossover conversion <turnout-crossover-conversion>
Crossover timber analysis and resolution <crossover-timbering>
Chair-position analysis and cache reuse <chair-analysis>
Model timber support and 2D chair layout <chair-support-and-2d-layout>
```

[GUI coverage](../gui-coverage.md) identifies the explanations still needed.
