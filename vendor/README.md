# Vendor note

`vendor/value-leakage` is a snapshot of https://github.com/adsingh-64/value-leakage
(commit recorded in this file when refreshed).

Upstream provides the Donation Bet replication code and shipped rollouts used for
offline forensics in this repo.

To refresh:

```bash
rm -rf vendor/value-leakage
git clone --depth 1 https://github.com/adsingh-64/value-leakage.git vendor/value-leakage
rm -rf vendor/value-leakage/.git
```
