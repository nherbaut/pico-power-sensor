HUGO ?= hugo
PYTHON ?= python3
BASE_URL ?= http://localhost:1313/
DEPLOY_REF ?= proto
GITHUB_REPO ?= nherbaut/pico-power-sensor

.PHONY: site-prepare site-build site-check site-serve site-deploy
site-prepare:
	$(PYTHON) scripts/prepare-site.py

site-build: site-prepare
	$(HUGO) --source site --destination ../public --baseURL "$(BASE_URL)" --minify --cleanDestinationDir

site-check: site-build
	$(PYTHON) scripts/check-site.py --base-url "$(BASE_URL)"

site-serve: site-prepare
	$(HUGO) server --source site --baseURL http://localhost:1313/

site-deploy:
	gh workflow run pages.yml --repo "$(GITHUB_REPO)" --ref "$(DEPLOY_REF)"
