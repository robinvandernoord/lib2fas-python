# Changelog

<!--next-version-placeholder-->

## v0.1.10 (2025-10-21)

### Documentation

* Support python 3.14; drop python 3.10 ([`ff16e5e`](https://github.com/robinvandernoord/lib2fas-python/commit/ff16e5e2dab94ebd17718b9c612514254f17acd4))

## v0.1.9 (2025-02-27)

### Fix

* Warn instead of crash if keyring is locked ([`2407a14`](https://github.com/robinvandernoord/lib2fas-python/commit/2407a14a072912e4945eabe177ea150fd7a03cc4))

## v0.1.8 (2025-01-12)

### Fix

* Return None for load_services if file doesn't exist instead of an exception ([`41a01a3`](https://github.com/robinvandernoord/lib2fas-python/commit/41a01a3c87364bd4fc251749e9de28e611e7617c))

## v0.1.7 (2024-04-10)

### Fix

* Don't crash on missing (supported) keyring ([`2624e2a`](https://github.com/robinvandernoord/lib2fas-python/commit/2624e2a216adff37a76ab16e215d7829d5ffef64))

### Documentation

* Link to 2fas cli tool ([`791286c`](https://github.com/robinvandernoord/lib2fas-python/commit/791286c64652ccf935643e255d579cda08e0ad02))


## v0.1.6 (2024-03-01)

### Fix

* Require the latest configuraptor, which includes a fix for 3.12 ([`bfae811`](https://github.com/robinvandernoord/lib2fas-python/commit/bfae811e0fdf46b0f9c80b823bbe020900740ed0))

## v0.1.5 (2024-02-29)

### Fix

* Import `secretstorage` for type hinting only (because the dependency is only installed on Linux by keyring) ([`ab87e47`](https://github.com/robinvandernoord/lib2fas-python/commit/ab87e472d427cb145dd8d0cac92d7b5f780131c9))

### Documentation

* Added more examples in readme ([`da25c64`](https://github.com/robinvandernoord/lib2fas-python/commit/da25c64fb3052ceb96ed5529cf5a3f866b0fd491))

## v0.1.4 (2024-02-28)

### Fix

* 'cleanup_keyring' now actually cleans up (removes old entries) ([`d072555`](https://github.com/robinvandernoord/lib2fas-python/commit/d0725551068d282658fd8767c7a13472bce9d351))
* Make more fields optional, as in the file standard ([`5c017cd`](https://github.com/robinvandernoord/lib2fas-python/commit/5c017cd66a205e6a37fe8c395406b8047ce5cd6b))

### Documentation

* **changelog:** Manually updated changelog to include the new /tmp behavior ([`b81e53d`](https://github.com/robinvandernoord/lib2fas-python/commit/b81e53d746ba3b142401e585805b37632df93649))

## v0.1.3 (2024-02-20)

### Fix

* Use tempfile to get temp dir, rather than assuming /tmp ([`b42ebc2`](https://github.com/robinvandernoord/lib2fas-python/commit/b42ebc22d49c9168b8e4c632141d486c04192210) by [@crmarsh](https://github.com/crmarsh))
* Revert linting changes to fixtures in 'tests' ([`8c717f5`](https://github.com/robinvandernoord/lib2fas-python/commit/8c717f5af25b9bea379aed2d6ee795b7cc5f7e36))

## v0.1.2 (2024-01-29)

### Fix

* **deps:** Remove cli-related dependencies ([`b2d0cce`](https://github.com/robinvandernoord/lib2fas-python/commit/b2d0cce1b0fc7eb347d5391a33d8bef07ebd5611))

## v0.1.1 (2024-01-29)

### Fix

* **load_services:** Made `passphrase` option as shown in the docs actually work ([`1ff6694`](https://github.com/robinvandernoord/lib2fas-python/commit/1ff6694e0e287768b5a8aad57e8b86993d65864c))

## v0.1.0 (2024-01-29)

### Feature

* Moved library code from 2fas to lib2fas ([`e4be2b7`](https://github.com/robinvandernoord/lib2fas-python/commit/e4be2b7303e92db4aad60fc51022dfaea96ad3ca))

## v0.1.0 (2024-01-25)

### Feature

* Cli tweaks and more pytests ([`01f8574`](https://github.com/robinvandernoord/2fas-python/commit/01f8574e527a60025e4e7b7bf0416a4e344fde2e))
* Started basic cli functionality ([`f15bbbf`](https://github.com/robinvandernoord/2fas-python/commit/f15bbbfe1d4e79ba644775dd1e4eb638e394dc81))
* TwoFactorStorage is now a recursive data type when using .find() ([`1f4847f`](https://github.com/robinvandernoord/2fas-python/commit/1f4847fa07eecd9c85623e5cb799a34ab3a8714d))
* Added tests and more general functionality ([`be86df5`](https://github.com/robinvandernoord/2fas-python/commit/be86df54cc4616541c6e636e882a1fa444af9d3a))

### Fix

* Improved settings menu + mypy typing + refactor ([`5d08f62`](https://github.com/robinvandernoord/2fas-python/commit/5d08f62daba7873e84766562c07370fa22018868))
* Improved settings tui ([`c0275b5`](https://github.com/robinvandernoord/2fas-python/commit/c0275b5d5e1b77fba77f65f3efdb5d117d9f5715))
* Include rapidfuzz in dependencies (previously only collected via 'dev' extra) ([`d2016e0`](https://github.com/robinvandernoord/2fas-python/commit/d2016e033ff00392032492525a3c4eb14a4432b3))
