# Press release (draft): Accountable AI experiments

Nov 20, 2026 · @Peter Zwart

Living copy: https://claude.ai/artifact/CRGLcUbT9nj4sLBxDoehsd (edit there; this file is a snapshot).

## Every action accounted for: Berkeley Lab scientists make AI-run experiments answerable for what they measure and what they skip

*Researchers state what may go wrong and how often; the AI agent then gives a reason for every site it measures and every site it leaves out.*

**BERKELEY, Calif. — \[Month day, 2027\]**

Cloud labs now run chemistry around the clock, and synchrotron beamlines at Department of Energy (DOE) light sources increasingly hand the overnight shift to an AI agent that decides where to measure next. Scientists at DOE's Lawrence Berkeley National Laboratory (Berkeley Lab) have made those agents accountable. With their approach, every action an autonomous experiment takes is certified: a site is measured because it was needed when the decision was made, and a site is skipped because a stated claim covers it, with a guaranteed limit on how often such skips turn out wrong.

### The problem: decisions without responsibility

AI-assisted experiments save beam time, samples and reagents, and they are here to stay. Yet they are usually treated as black boxes. The agent chooses, the map comes out, and no one can say which of the skipped measurements would have changed the answer, or how often. In a laboratory run by people, every shortcut has an owner: a protocol states the rules, a colleague can explain a choice, and the record can be audited. The agents now taking over those choices deserve the same standard.

### The solution: a contract, and a reason for every choice

Before the experiment starts, the researcher writes a short contract: what counts as safe to leave out, how close a prediction must come to the truth, and how much may go wrong. The statistical framework turns that contract into the agent's decisions, and keeps a small random check on its work along the way. The agent remains free to use any AI model it likes; the contract governs what it may do with it.

The outcome is a campaign that can account for itself, site by site:

- **Measured, because it was needed:** no claim could vouch for the site when the decision was made.
- **Skipped, because a claim covers it:** the site holds nothing of interest, or its result can be predicted within tolerance, and the share of such skips that go wrong stays within the agreed limit.

Every choice, to measure or not to measure, is written into a record that can be checked afterwards.

### Not faster, but as promised

Accountable campaigns are not more efficient than today's AI-guided ones, and in some settings they measure a little more. What they offer is a promise that holds. Tested on scans that had been measured in full, so that every skip could be checked, the campaigns stayed within their agreed limits as often as promised. A conventional AI-guided run on the same data, trusting its own error bars, was wrong about six times as often as those error bars predicted, and nothing in the run could have shown it.

“We expect a colleague to answer for every shortcut they take, and an AI agent running an instrument should meet the same standard,” said Peter Zwart, a staff scientist in Berkeley Lab's Molecular Biophysics and Integrated Bioimaging Division, who led the work. “Think of it as a licensed, bonded and insured AI agent. The rules are written down before it starts, the risk it may take is capped, and the cap is backed by a guarantee anyone can check. It costs a little efficiency. In return, you get what you asked for.” *\[Draft quote for approval.\]*

“I hand the night shift to the agent and agree on one thing in advance: how much I can afford to have wrong. In the morning I know what was measured, what was skipped, and why, and I can stand behind the map,” said *\[future user: a beamline scientist at a DOE light source\]*. *\[Hypothetical user quote, as in a working-backwards draft; to be replaced by a real user after the first deployment.\]*

### What's next

The team has developed the theory and demonstrated that the guarantees hold. The next step is to put the approach to work on autonomous instruments across the DOE complex, from X-ray beamlines at light sources to self-driving synthesis laboratories, starting with a pilot synthesis campaign.

The study, “Accountable experiments: autonomy under contract,” appears in *\[journal, date\]*; co-authors *\[names\]*; supported by *\[funding\]*; software and data at *\[repository\]*. **Media contact:** *\[name, email\]*.

---

*Working-backwards document: a future press release written to guide the paper. Quotes are drafts; the user quote is hypothetical.*
