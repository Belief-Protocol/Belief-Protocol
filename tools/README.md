# tools

`belief_build.py` packages a belief folder for every major AI platform. See the
[Build Tool](../README.md#build-tool) section of the spec for what it does and when it fails.

```
python3 tools/belief_build.py path/to/belief-folder --draft     # while drafting
python3 tools/belief_build.py path/to/belief-folder             # to ship (needs `url` in BELIEF.md)
```

Then host `dist/BELIEF-FULL.md` at the `url`, and follow `dist/INSTALL.md`, including the tests.

Exit codes: `0` built, `1` failed (nothing written), `2` built as a draft (don't install).
