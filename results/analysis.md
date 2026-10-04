## Caught for the right reasons

A catch counts here only if, for each of P, U and E, at least one tool the checker labelled with it also has it in our labels.

| Checker | Trifectas caught | With the right reason for all three | Caught with partly wrong reasons |
| --- | --- | --- | --- |
| lethal-trifecta-lint | 2 | 1: github-alone | playwright-alone |
| mcp-trifecta | 5 | 2: github-alone, supabase-alone | slack-alone, playwright-alone, git-fetch |
| triflow | 3 | 1: github-alone | supabase-alone, playwright-alone |

## Capability recognition on 180 unique tools

Found = tools with the capability in our labels that the checker also gave it. Extra = tools the checker gave it that we did not.

| Checker | P found | P extra | U found | U extra | E found | E extra |
| --- | --- | --- | --- | --- | --- | --- |
| lethal-trifecta-lint | 25/96 | 14 | 13/57 | 22 | 19/37 | 21 |
| mcp-trifecta | 22/96 | 11 | 8/57 | 17 | 4/37 | 15 |
| triflow | 18/96 | 0 | 15/57 | 18 | 3/37 | 2 |
