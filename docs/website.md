# Documentation website

This project adapts NoiseNet's Hugo layout and CSV tracking workflow. Markdown and CSV files in the source tree remain authoritative. GitHub Actions builds and publishes the site on pushes to `master`, with manual deployment also available. No Node.js or external Hugo theme is required.

```sh
make site-build
make site-serve
make site-check
make site-check BASE_URL=https://nherbaut.github.io/pico-power-sensor/
```

Requirements: Hugo 0.165 or newer, Python 3 and Make. `.build/site/` and `public/` are generated and ignored. Run `make site-prepare` after source changes during a live preview.

The preparation script publishes project Markdown and hardware tables, copies explicitly linked design artifacts and rejects links outside the project or into excluded local/secret files. Procurement and inventory are empty until actual transactions are recorded.

## Hardware images

The homepage embeds front PCB PNGs of both boards. Each board page also embeds the current electrical schematic PNG, with full-size links and the original PDF/SVG/CAD downloads. Images scale to the screen, have descriptive alternative text and captions, and can be opened at full resolution without JavaScript. PNGs are drawings from CAD, not photos or bench results.

```sh
make hardware-images
make site-check
```

`make hardware-images` reads the current KiCad schematic and PCB files into temporary exports and refreshes only the PNGs and their provenance manifests. It does not regenerate, reroute or change either board. Electrical schematics use a white background and 8000 pixels on the longest side; front PCB PNGs are 1800 pixels wide. Inline electrical schematics use 2200-pixel previews linked to the full 8000-pixel drawings. This rendering step needs KiCad CLI, Poppler's `pdftoppm` and librsvg's `rsvg-convert` in addition to Python and Make.

After changing a design, use `make hardware-export` or `make carrier-export` to run that board's checks and refresh its PDF/SVG/PNG drawings and review archive together. Save manual edits before using any **build/generate** target, which replaces CAD rather than only exporting it.

Commit the PNGs and `images.json` manifests alongside their board artifacts. Normal Hugo builds and CI require only Hugo, Python and Make; they do not invoke KiCad or image renderers. Site preparation verifies CAD/image hashes and fails with a refresh instruction if a drawing is stale or has been altered. Internal image and full-size links also respect the configured GitHub Pages subpath.

## GitHub Pages publication

The workflow is [.github/workflows/pages.yml](https://github.com/nherbaut/pico-power-sensor/blob/master/.github/workflows/pages.yml). It uses Hugo 0.168.0 to run `make site-check`, uploads `public/` as a Pages artifact only after the build and link checks succeed, then deploys using GitHub's Pages actions. The base URL comes from GitHub Pages configuration, so project subpaths and configured custom domains are respected. Deployment is restricted to `master` and uses the `github-pages` environment.

To enable publication:

1. In [repository settings](https://github.com/nherbaut/pico-power-sensor/settings/pages), select **Settings → Pages → Build and deployment → Source → GitHub Actions**.
2. Commit and push reviewed project sources to `master`, including the workflow, PNGs and image manifests. Each push builds and deploys automatically; generated `.build/` and `public/` directories remain ignored.
3. Check **Actions → Publish documentation to GitHub Pages** for the build result and deployment URL. Unless a custom domain is configured, the site will be at [nherbaut.github.io/pico-power-sensor](https://nherbaut.github.io/pico-power-sensor/).

You can also select **Run workflow** on `master` from GitHub Actions, or run `make site-deploy` with an authenticated GitHub CLI. Its defaults are `GITHUB_REPO=nherbaut/pico-power-sensor` and `DEPLOY_REF=master`. No personal access token or deployment secret is required by the workflow; the deployment job uses GitHub's built-in token and OIDC permissions. See [Hugo's GitHub Pages guide](https://gohugo.io/host-and-deploy/deploy-to-github-pages/) for the hosting setup.

Adding this workflow locally does not publish the site. Publication begins after the sources are pushed and GitHub Pages is enabled.
