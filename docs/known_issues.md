# Known Issues

## Current Issues

- CLIP score is semantic similarity, not absolute visual quality.
- Context Program does not yet have strict schema validation.
- Provider-specific prompt compilers need more tests.
- Runtime output files should not be treated as curated demo assets.
- Some model integrations depend on local environment variables and external availability.

## Resolved Issues

- CLIP feature extraction now uses model feature tensors instead of model output objects.
- CLIP evaluation prompt is separated from generation prompt to avoid token overflow.
- Debug reports now make prompt lifecycle easier to inspect.

## Future Work

- Add schema validation.
- Add provider compiler test suite.
- Add dashboard-level issue tracking.
