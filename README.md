# BoydRicherson2009

From-scratch, independently reviewed replications of two 2009 papers by
Robert Boyd and Peter J. Richerson on cultural group selection. Each
paper gets its own subfolder — distinct models, distinct questions, one
common theme.

## Contents

- **[culture_human_cooperation/](culture_human_cooperation)** — Boyd &
  Richerson (2009), *Culture and the evolution of human cooperation*
  (Phil. Trans. R. Soc. B). A minimal model of migration vs. local
  cultural selection on a 256-subpopulation torus, illustrating why
  culture can sustain far more between-group variation than genetics
  typically can.
- **[voting_with_feet/](voting_with_feet)** — Boyd & Richerson (2009),
  *Voting with your feet: payoff biased migration and the evolution of
  group beneficial behavior* (J. Theor. Biol.). A two-subpopulation
  model of payoff-biased migration ("voting with your feet"), asking
  when this process reliably spreads the group-beneficial norm.

Both follow the same pattern as this author's other named-paper
replications (e.g.
[AckleyLittman1994](https://github.com/doesburg11/AckleyLittman1994)):
standalone, from-scratch implementations built directly from each
paper's text, with no author-released code to check against, and
reviewed by an independent model (OpenAI Codex) before being finalized.
See each subfolder's own README for its model, calibration notes, and
results.

## How The Two Papers Relate

### In Common

- **Same authors, same year, same overarching theme**: how cultural
  group selection can work, given that ordinary group selection theory
  says migration between groups usually erases the between-group
  variation selection needs to act on.
- **The same core mechanism**: a tug-of-war between local adaptation
  (which creates/preserves differences between groups) and migration
  (which erases them). Both models live or die on that one ratio.
- **Both use "multiple stable equilibria when common"** as the engine
  of persistence — a trait/behavior is locally self-reinforcing once
  it's the majority, which is what lets migration have a threshold
  effect rather than a smooth one.
- **Both conclude that culture, specifically, can sustain conditions
  genetics generally can't** — fast local cultural adaptation (learning,
  conformity) and assimilation (migrants adopting local norms) push the
  effective ratio into the regime where variation survives.
- **Both are explicitly illustrative toy models**, not attempts at full
  realism — stripped down to isolate one mechanism each.
- **Neither was released with code** — both had to be built from the
  paper's text alone.

### Where They Differ

| | `culture_human_cooperation` | `voting_with_feet` |
|---|---|---|
| **Structure** | 256 subpopulations on a 16×16 torus, nearest-neighbor migration | Just 2 subpopulations, fully connected |
| **Traits** | 3 independent binary traits (8 possible local states) | 1 behavior, continuous frequency |
| **Migration** | Unbiased — fixed rate `m`, pure diffusion | **Payoff-biased** — migration rate itself depends on which side currently pays more (`mu` controls the bias strength). This is literally the paper's title mechanism. |
| **Population sizes** | Fixed per site — only composition changes | **Sizes themselves evolve** — migration literally moves people between the two groups, so relative population size (`p`) is a dynamic variable, not a constant |
| **What's tracked** | Which of 8 arbitrary combinations dominates locally — no combination is "better," just different | One behavior is explicitly defined as higher-payoff-when-common ("group-beneficial") — the model asks whether *that specific one* wins |
| **Question asked** | *Does variation between groups persist at all?* | *Given that it can persist, does selective migration actually spread the better norm — or just amplify whichever group started bigger?* |
| **Equations given by the paper** | None — only qualitative description + one figure. We had to choose our own discretization and calibrate against the figure. | Full closed-form equations (1-9), specific worked parameter values, several numbers to check against directly |
| **What we found under scrutiny** | The paper's own `m/s` thresholds don't transfer literally to our discretization; middle ratios are seed-dependent, not deterministic | Two real OCR errors in the equations (both independently confirmed); and a nontrivial gap between "more migration spreads the good *label*" and "more migration raises actual *welfare*" |
| **Real-world grounding** | Cites actual primate dispersal/selection numbers (~25% migration, ~1% selection) as a contrast case | Purely illustrative parameters (no biological/anthropological numbers attached to `d`, `h`, `g`) |

The cleanest way to see the relationship: **the culture paper is the
general theory** (variation between groups can persist if `m/s` stays
low enough, and that's culture's whole trick), and **voting-with-feet
is a specific, more skeptical follow-up question** — okay, suppose
variation *does* persist, does the specific mechanism people usually
point to (migration toward better places) actually deliver the
improvement it's credited with, or can the same tug-of-war just as
easily spread the worse option if the "wrong" group happens to be
bigger?

## References

- Boyd, R., & Richerson, P. J. (2009). Culture and the evolution of
  human cooperation. *Philosophical Transactions of the Royal Society
  B*, 364(1533), 3281-3288. https://doi.org/10.1098/rstb.2009.0134
- Boyd, R., & Richerson, P. J. (2009). Voting with your feet: payoff
  biased migration and the evolution of group beneficial behavior.
  *Journal of Theoretical Biology*, 257(2), 331-339.
  https://doi.org/10.1016/j.jtbi.2008.12.007
