# Timestamp vector

`hello-world.txt` and its receipt are from [OpenTimestamps](https://github.com/opentimestamps/opentimestamps-client/tree/cd71c7609421bed2a07b9642a3c02a58c9fd2cdf/examples).
`block-358391.hex` is the [Bitcoin header](https://blockstream.info/api/block/000000000000000003e892881a8cdcdc117c06d444057c98b6f04a9ee75a2319/header), retrieved on 2026-09-28.

Tests supply this header through a fake node; live verification requires Bitcoin
Core. The vector checks receipt parsing, Merkle operations and the attested time.
