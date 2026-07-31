# Morphology Release Integration

## Contract

`tamil-morphology` is the source and release authority. Each GitHub Release
publishes one versioned source/runtime archive containing:

- `manifest.json` with the release version and SHA-256 digest of every runtime
  artifact;
- `runtime/*.fst` and the auxiliary inventory sidecar;
- rebuildable source, tests, documentation, statistics, and provenance.

Consumers commit a morphology lock and the exact runtime files they ship. They
must never download an unversioned model during application startup or model
training. Reproducibility requires updates to be explicit Git commits.

## Consumer Update

After downloading a release archive:

```bash
python3 scripts/install_morphology_release.py \
  tamil-morphology-0.1.0-rc3.tar.gz \
  --runtime-dir tamil_morph_tokenizer/data/fst-models \
  --lock-file morphology.lock.json
```

The installer rejects path-traversal links, requires one manifest, verifies all
artifact hashes before writing, replaces files atomically, removes stale FST or
JSON runtime files, and writes the verified manifest as the consumer lock.

## Automatic Updates

Use a scheduled or `repository_dispatch` GitHub Actions workflow in each
consumer:

1. Query the latest `kupilikula/tamil-morphology` GitHub Release.
2. Stop if its version already matches the committed lock.
3. Fetch the newest version tag with a dedicated read-only deploy key scoped
   to the private morphology repository.
4. Run `install_morphology_release.py`.
5. Run the consumer's full test suite.
6. Open a versioned update pull request containing the runtime files and lock.
7. Optionally enable auto-merge only after required CI checks pass.

For private repositories, register one read-only deploy key on
`tamil-morphology` and store its private key as the `MORPHOLOGY_DEPLOY_KEY`
Actions secret in each consumer. This grants no write access and no access to
unrelated repositories. A GitHub App is preferable if the repositories later
move to an organization.

Each consumer repository must give its `GITHUB_TOKEN` read/write workflow
permissions and enable **Allow GitHub Actions to create and approve pull
requests**. That token writes only the tested update branch in its own consumer
repository; it is separate from the read-only morphology deploy key.

Do not have consumers track a mutable `latest` URL at runtime. An automated,
tested lock-file PR provides the same operational convenience while preserving
rollback, auditability, and reproducible training runs.
