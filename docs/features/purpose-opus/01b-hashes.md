---
feature: purpose-opus
phase: pre-registration
status: frozen
created: 2026-10-19
---

# 01b. Pre-registration — fixture hashes

Part of the frozen pre-registration with [01-fixtures.md](./01-fixtures.md) (which states the task-spec hash) and [01a-rules.md](./01a-rules.md). sha256 of every file in the eight new fixture dirs, LF line endings. `tests/unit/test_eval_purpose_opus_fixtures.py` recomputes this table (CRLF normalized to LF) and fails on any difference, added file or missing file.

Recompute: `cd evals && find fixtures/web-hpa-maxreplicas fixtures/checkout-postmortem-1012 fixtures/price-build-kwd fixtures/orders-restore-runbook fixtures/android-260-release fixtures/checkout-flag-rollout fixtures/logo-2026-swap fixtures/api-hpa-maxreplicas -type f | sort | xargs sha256sum`.

| file (under `evals/`) | sha256 |
|---|---|
| `fixtures/android-260-release/CHANGELOG.md` | `4869676863ff0ffbf4a07d3a0324f237c2033ac11a9c0ab2cade44876578773c` |
| `fixtures/android-260-release/README.md` | `14976fd635704e8a23cf431317fe427b0649c8701206f0454e5e4b39ef74f461` |
| `fixtures/android-260-release/app/build.gradle` | `444b99c9a575a9cece4a73629ccdc596d23cd78adeb5ce3841ba3d8da55e4d62` |
| `fixtures/android-260-release/app/proguard-rules.pro` | `d2930182c87f1f1d1263a70a9aaa2c036994072faf746714bbe212a670ebaf78` |
| `fixtures/android-260-release/app/src/main/AndroidManifest.xml` | `0ca30b4e90632e5b21a1427208aa375d4f5322e0c87376b75017d3fe975880a2` |
| `fixtures/android-260-release/app/src/main/java/com/example/tally/MainActivity.kt` | `3e762234c82c661a3cef953d32b13522dd8636cfde0e87b5754cec934888d804` |
| `fixtures/android-260-release/build.gradle` | `9b92a3593524c64bfa6454de3cc487b71b2d7825d95ad55522d422d2b27a4fbb` |
| `fixtures/android-260-release/gradle.properties` | `a62205638a2d8b28a3e1ce6ac769e6e58f615572b4e4769031eead1d3b6beea8` |
| `fixtures/android-260-release/gradle/libs.versions.toml` | `a71aa26512a4d066b9ea0797264a98b9510590ac8bdd597181488e5db15ade92` |
| `fixtures/android-260-release/release/play-console-artifacts.csv` | `d3546422651012d81b2c57a7385364d619848427a7095f8a6c97505a6bb7c5c8` |
| `fixtures/android-260-release/settings.gradle` | `3ee7aeda77928d734bd06fc961152ddaa2db0d1fc19c7478b77ed873a340055a` |
| `fixtures/api-hpa-maxreplicas/README.md` | `c48e3c896871005575281c1dcbc3b392d10c4decd2274d09f0c17f374f9a9acb` |
| `fixtures/api-hpa-maxreplicas/db/api-db/postgresql.conf` | `f9ba45e779bb078e569cd25842eb11adac3cc7aa01d4d25585de024a686d53d4` |
| `fixtures/api-hpa-maxreplicas/deploy/api/configmap.yaml` | `f10a4f20784556063f0cdd91a4267fbc2af9a3959c779c15e94ab3d10ecad162` |
| `fixtures/api-hpa-maxreplicas/deploy/api/deployment.yaml` | `643cb00e0b1a6fa42915b062750eb873f3195974643080ac805b86de0e0da719` |
| `fixtures/api-hpa-maxreplicas/deploy/api/hpa.yaml` | `178a700560f698d4aa9dcca40f7927fed3360a212c939bb71ee53393bf8ed665` |
| `fixtures/api-hpa-maxreplicas/deploy/api/service.yaml` | `ea43972251178b0a19961407db738194166a41f961b0589c7a2081c0bdb04ee3` |
| `fixtures/api-hpa-maxreplicas/deploy/db-proxy/deployment.yaml` | `694f9ec6eb01c5ffe370489a0be51be7911bc9f1fd4f26d4ff502e6c4c1e3a8c` |
| `fixtures/api-hpa-maxreplicas/deploy/db-proxy/pgbouncer.ini` | `68af15e966346bd9d62335eff38da38bdfda7858b3e2d9f7495b8171a8cfc3f7` |
| `fixtures/api-hpa-maxreplicas/deploy/db-proxy/service.yaml` | `3f43d2d73cf3bf5a746d8b793af2af73ddfbf47266b9b77db9ab81dcd4d33b1c` |
| `fixtures/api-hpa-maxreplicas/deploy/kustomization.yaml` | `e61b03a5acca3b39c9a34431954eca699041d6405bec1981e8eb98f832daf37b` |
| `fixtures/api-hpa-maxreplicas/deploy/worker/deployment.yaml` | `8220e2835740c8f0adeeddb3cf0f394d1a364ae4c5a034674d6356d1caabe348` |
| `fixtures/api-hpa-maxreplicas/loadtest/2026-09-18.md` | `c7aa2937e483fe60007e5124beb741c95a1f861d4d0e9ad27969552c55a88a4c` |
| `fixtures/checkout-flag-rollout/README.md` | `22320fbacef18e92daa2fee2b4d33998e394b8a78208b51fccb8aaf01a396b0b` |
| `fixtures/checkout-flag-rollout/flags/README.md` | `00f510d431981652d737d4c7bfb4e9a68138e24d3bb20bc0317cca8bd253d14e` |
| `fixtures/checkout-flag-rollout/flags/effective.py` | `bf10f09b9b7820ec7ebceedc720b19c108a0ad098323751e0079c72be35a9740` |
| `fixtures/checkout-flag-rollout/flags/policy/regions.yaml` | `5a0359e74b21e667b19fba25b4d4c6aecf0baab406855e1aab0baf67ecc9fe41` |
| `fixtures/checkout-flag-rollout/flags/production.yaml` | `6b6bd8966ed75998b830b27ff9bfc30dbe1da4df28ea94446d9a9dc42ed8bf1a` |
| `fixtures/checkout-flag-rollout/flags/staging.yaml` | `2fe45ed6f62973dd1ea607fc80dafa3c1e3c5d5c420cb3357886babd34741e1e` |
| `fixtures/checkout-flag-rollout/service/flag_service.py` | `8ca7e13fcf917b4774bfda0abce9ec80c372344abe48f5387889697483b9d495` |
| `fixtures/checkout-flag-rollout/tests/test_flags.py` | `741f0c79c90dc569f8cdd1547cf1c6ac5337faf71fc1746e1b58f98986942599` |
| `fixtures/checkout-postmortem-1012/README.md` | `baa2e861bac625ecf7599a27ecb9000ca09d2f0d94e6fd457455e8bbd1e0e1b6` |
| `fixtures/checkout-postmortem-1012/incident/channel.txt` | `5ab94d11868076cf5dadf4192cbcaa40947a8846e5964969b6d74deafec6d4d1` |
| `fixtures/checkout-postmortem-1012/ops/audit/2026-10-11.txt` | `9ecee61209cd66f8716d2baa43b129589885415356965f3adc5d43c039360b78` |
| `fixtures/checkout-postmortem-1012/ops/audit/2026-10-12.txt` | `5b7be0a0095f58ec3ccc1a6008ba6744feaf2f2570ceacbdb4bb898ce07622f1` |
| `fixtures/checkout-postmortem-1012/ops/exports/checkout-5xx-2026-10-12.csv` | `b802101b1e353747de90b2a4abf59615df5b86d3e1d46121acc4bd8a43cb544d` |
| `fixtures/checkout-postmortem-1012/ops/exports/search-p95-2026-09-03.csv` | `57263aa779d150d43275dfb5ed6d8457250428c30c7c0b8d18f7848033b743e2` |
| `fixtures/checkout-postmortem-1012/postmortems/2026-09-03-search.md` | `1dc2df3a0a3703d332b1b70918c714b6db2fd3b788226b1fc2b9d928c7b7783e` |
| `fixtures/checkout-postmortem-1012/postmortems/2026-10-12-checkout.md` | `eb33c15d55728bbc707ddec3ab07e40f018b3c5b8dfa3563de7a1c37723af62b` |
| `fixtures/checkout-postmortem-1012/postmortems/TEMPLATE.md` | `25cdfede594271aaa927ac6f696269b2dcf7daeb63cc56c4e485ac805c528c8e` |
| `fixtures/checkout-postmortem-1012/runbooks/checkout.md` | `e6eaf45e4a577bd548e5a605eb621f0edb6accbb5da42719b3b0a14491d4de87` |
| `fixtures/checkout-postmortem-1012/runbooks/search.md` | `ffceed0ba34f4354e0c0a897eb4b853714ec54ec9d492f066b42c82263aa7b7c` |
| `fixtures/logo-2026-swap/README.md` | `228dc228d58e27b8f9a96a38acf719f7ea6b8f2912983d1646f9c169a75888da` |
| `fixtures/logo-2026-swap/design/README.md` | `f4d451773315b7873cf08497a893620534068987e0d61c83c1b1e037db3fe948` |
| `fixtures/logo-2026-swap/design/exports/logo-2026-mono.svg` | `56b495c5eead3bc875fb508b28c321d08277cd0fd4931660a2b9fc075892ef4c` |
| `fixtures/logo-2026-swap/design/exports/logo-2026.svg` | `d3a4cb47a23c5dacad5431c4d9e0a649e313af0180d235fa3ef65e8d6f883c3d` |
| `fixtures/logo-2026-swap/infra/cdn/README.md` | `0aa89531e48987540d6aa4f9ccf1eea3e9b0b18f64fb32b1d2997f47285aa8ed` |
| `fixtures/logo-2026-swap/infra/cdn/cache-rules.json` | `a63bfa4d401dbd0e10d5d8146c2ede906abc012c94ace113b63203b2a30d1a09` |
| `fixtures/logo-2026-swap/web/app.py` | `e13f13f6648e43a29a378bd99f9ff7bd9e2b401610c64c54a6793284b4b3e69c` |
| `fixtures/logo-2026-swap/web/assets/fingerprint.py` | `e2c8739d0f51b314a5d6ccf4ef57f1f84c6d10ae5ea7da16a046424c4954ad45` |
| `fixtures/logo-2026-swap/web/static/assets.json` | `8c77f575219413cd653fbf3a5c5adea06dcc90459a91cd6d3b097a3d61a068bb` |
| `fixtures/logo-2026-swap/web/static/css/site.css` | `2c55e8e3c4c955ccc1c21163e7c1e5d53f6738b31a569907ad057b249d313f48` |
| `fixtures/logo-2026-swap/web/static/img/icon-cart.svg` | `71e92a45cee2e8e1c44329697901ce6877285570952855d5d6e211a1789a7c0a` |
| `fixtures/logo-2026-swap/web/static/img/logo.svg` | `ba50e1359b6135ef48357162741a28183fe5f408e4848c8e2dd532fbe4f119a7` |
| `fixtures/logo-2026-swap/web/static/js/app.js` | `07e9e867f8ac3af35001da64b63f4b405e3281b52e8cb3956de56d59a6f329b7` |
| `fixtures/logo-2026-swap/web/templates/base.html` | `7388976ac9e1b23d225869e75fb5a97818e7d1382007dc94efbb5dde0322fa6e` |
| `fixtures/logo-2026-swap/web/templates/index.html` | `555111c2b29ceb2e47b7446455fbbaaa5e2f8f6c9affe3b7eb27662d2a1c337c` |
| `fixtures/orders-restore-runbook/README.md` | `620d949f05713ff3e911431f11cbfca2a246e472d5db160966103d04e11d038d` |
| `fixtures/orders-restore-runbook/backup/README.md` | `f703e271723dcfd1753dabfb3fb9029d65ef4bcd436304e938d6b2bdc2bb4a1b` |
| `fixtures/orders-restore-runbook/backup/events_export.py` | `4d444c8f4c586d40c933d7f7162bedb91a4617413e480dd15528b702fdc44c54` |
| `fixtures/orders-restore-runbook/backup/exclude.conf` | `c1a1d90e4b5ce2791a9ec6bf8eb08ea253ac2afb7a25663415fac8e6c6a79abd` |
| `fixtures/orders-restore-runbook/backup/nightly.sh` | `271ec1b249759ec0aa1463b052bb83061fa4cadd6118a6b4b7e4f785290cef2c` |
| `fixtures/orders-restore-runbook/db/schema.sql` | `684a909e0477b72c80de471193511a51b632b8e094b17ab2d6fdd4635b9339e0` |
| `fixtures/orders-restore-runbook/deploy/jobs/events-export.yaml` | `fd0cd3824e412994cbc71dfeae12a99ca0c341d02b7a0000b11226d760eac458` |
| `fixtures/orders-restore-runbook/deploy/jobs/report-daily.yaml` | `6fd10b09cc2220f81f73e7d90da40275909236ba0195b253f1339e90cd19e876` |
| `fixtures/orders-restore-runbook/ops/cron/backup.cron` | `d25704b7760d75ebed3b0af54bf0399131a5cfbd505c1d915e71ec36add130c8` |
| `fixtures/orders-restore-runbook/ops/cron/maintenance.cron` | `107f0528af03e5e002c2d5e62504d332e79eefcac70bbdcaadf37ff14bc34cb7` |
| `fixtures/orders-restore-runbook/runbooks/orders-failover.md` | `dd206e9d45105df9a8ad3f0d6d7fafc36ced88451211c95bdc23e9b21c9f49ab` |
| `fixtures/orders-restore-runbook/runbooks/orders-restore.md` | `0545e066a4e0ef84f3572fc94ec73de99b01b0f1e9ef5ce78a633e0432b3a70c` |
| `fixtures/price-build-kwd/README.md` | `2126821cc43b4c244a241e1f3b3f8e8d309f6c26efde1988bee2bb8c1916aec6` |
| `fixtures/price-build-kwd/build_prices.py` | `7102697a92e6ca1cebc87096f6390577e3a2cf4f8cdfd9c6c6ba0b8b21d34f62` |
| `fixtures/price-build-kwd/checkout/__init__.py` | `437b1bd7a30d1567c4669bca423f23ca5fb92958c11bb942e16926715190b090` |
| `fixtures/price-build-kwd/checkout/charge.py` | `945de07ba4f3669da9d555ec692aaa6095e0ac6a8a7cd70f921c096193730698` |
| `fixtures/price-build-kwd/conftest.py` | `c994b3a07fe17eee8af161bd9cf8689b97fcc689e65e57576904113fd7d69787` |
| `fixtures/price-build-kwd/out/prices.json` | `563405f18e32e382be31c30cc6021db8977a08836e0627eed12a104b749dab3f` |
| `fixtures/price-build-kwd/prices/eur.csv` | `926a4d0650e0893193444895178c3ea440c184531a8860e89ea8341ae6eae5c1` |
| `fixtures/price-build-kwd/prices/gbp.csv` | `fe288f1571abb3ed1ae98f2fc804c58b72c14676c11a48871851018dc92a329c` |
| `fixtures/price-build-kwd/prices/kwd.csv` | `befbcede59b85df3f513ec70f8a9d3989acaa188e979882fc270483b09b57ba9` |
| `fixtures/price-build-kwd/prices/usd.csv` | `de5e8614f8d599badf19f8f25540114d9ab496c675026bc96de50f4d06713915` |
| `fixtures/price-build-kwd/tests/test_build_prices.py` | `e2af821ab06e6ec57c54c505c8287e9746ca887ca40464d65aef87a018a6e407` |
| `fixtures/price-build-kwd/vendor/__init__.py` | `8304b95ea43a245d928411824f57f19a7dbd65ccc78b223dd5668800dfbf2f76` |
| `fixtures/price-build-kwd/vendor/payrail/__init__.py` | `58800c4ed785d928664890240e5ef4f1b0a089b9a764dd751c1d3e1a36237aa7` |
| `fixtures/price-build-kwd/vendor/payrail/client.py` | `c9f7d4ede5bd68195c10ca5563f904e7be8504b8ff4af1a961d919022d7d61fe` |
| `fixtures/price-build-kwd/vendor/payrail/docs/amounts.md` | `7a59359379e1c23e912da4c6a93d098aaef57b2ee3915f4e1ef9c127977f72c3` |
| `fixtures/price-build-kwd/vendor/payrail/docs/errors.md` | `82b75d111e7648181dd0658d1e2ac476bc93518234d23bc977eff718e42110ca` |
| `fixtures/price-build-kwd/vendor/payrail/docs/refunds.md` | `5debe82d3e3159db2fa4c01f2ba4aed3487e35f243d976c098cfafde00310942` |
| `fixtures/web-hpa-maxreplicas/README.md` | `c928b1276818fbf2f1cd1ff3bb1ae77d6a5f903c4f47d14b3bd996b419ae6d27` |
| `fixtures/web-hpa-maxreplicas/db/orders-db/pg_hba.conf` | `48a82c371e97eff1c4296c02c21a894f78389256d4976a32512ae86ed4baf024` |
| `fixtures/web-hpa-maxreplicas/db/orders-db/postgresql.conf` | `5bec7d9b2515b602730648a1ea42e1b7ea2ba79828ad47a4ab2e5c39149b5143` |
| `fixtures/web-hpa-maxreplicas/deploy/kustomization.yaml` | `a0a5c2ef68f6f93de78ac976a3bbc88caf684bc2d9eb30c47ced7e9d3b24108f` |
| `fixtures/web-hpa-maxreplicas/deploy/search/configmap.yaml` | `839ed1f8da773d866450002c35cab8ba7eb51109a0cc96fbd8850814d618e38c` |
| `fixtures/web-hpa-maxreplicas/deploy/search/deployment.yaml` | `d93c6c613bc68fe4a240b64b5f3626708010fb154cd3b9468b7d343e3d1cbb7c` |
| `fixtures/web-hpa-maxreplicas/deploy/search/service.yaml` | `ab6206b53d4ed35d5fe39ad04aaf5abbec65846bb6b1ad8020b64cfc9529b1a4` |
| `fixtures/web-hpa-maxreplicas/deploy/web/configmap.yaml` | `edc65461794bc95fa3068c62e70c341a4d9300ff0c92cecf3358d6d760cd2fad` |
| `fixtures/web-hpa-maxreplicas/deploy/web/deployment.yaml` | `5a85344760994072a07208c33392f6ec5491076a953e52def026643b4636a555` |
| `fixtures/web-hpa-maxreplicas/deploy/web/hpa.yaml` | `e02afb03fe7b4e0af796d4da12d54f30b4537289fc7395b155ec995e47e471ba` |
| `fixtures/web-hpa-maxreplicas/deploy/web/service.yaml` | `d3688d4b9bfae8883a80c5cb1aa266a0c33725c0ce83eb462fc85cf87a76a433` |
| `fixtures/web-hpa-maxreplicas/deploy/worker/configmap.yaml` | `434b84ffe1422422bd420e786a1f7d275d3cbaa2f8e9f6cb8b594774fc02c057` |
| `fixtures/web-hpa-maxreplicas/deploy/worker/deployment.yaml` | `60e286c1db80576d33473a3a0aac0dc6ec4d41dae0fb8ebb209243f90d32dc3d` |
| `fixtures/web-hpa-maxreplicas/deploy/worker/hpa.yaml` | `9cccc8842c97102e13d1e4f7d99061a902f7292a1cbbba5f42b189f3855e3300` |
| `fixtures/web-hpa-maxreplicas/loadtest/2026-10-02.md` | `7f341c1924092a53c28542350420cf9aff7f4f9733f7f5f12be459353d30ac13` |
