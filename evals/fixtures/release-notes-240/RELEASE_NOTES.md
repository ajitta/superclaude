# tidepool release notes

## 2.3.0 — 2026-08-27

### Breaking

- `tidepool serve --port` takes a single port; port ranges (`8000-8010`) are rejected at startup. (#184)

### Added

- `tidepool export --format parquet`. (#188)
- `storage.compression` setting (`zstd` default, `none` to turn it off). (#190)

### Fixed

- Two workers flushing the same batch no longer write duplicate rows. (#195)
- `tidepool status` exits 1 when the scheduler is down. (#197)

## 2.2.1 — 2026-07-30

### Fixed

- Parquet files written on Windows had a corrupted footer. (#181)
