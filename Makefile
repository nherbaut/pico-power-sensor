HUGO ?= hugo
PYTHON ?= python3
BASE_URL ?= http://localhost:1313/
PORT ?= 1313
GH ?= gh
GITHUB_REPO ?= nherbaut/pico-power-sensor
DEPLOY_REF ?= master
BOARD ?= interposer
GATE ?= fabrication

.PHONY: help site-prepare site-build site-serve site-check site-deploy

help:
	@echo "make site-build                         Build the website in public/"
	@echo "make site-serve                         Preview at http://localhost:1313/"
	@echo "make site-check                         Build and check internal links"
	@echo "make site-deploy                        Trigger GitHub Pages deployment (DEPLOY_REF=master)"
	@echo "make site-build BASE_URL=https://USER.github.io/REPO/"
	@echo "make hardware-generate                 Regenerate draft files (overwrites hand edits)"
	@echo "make hardware-build                    Generate, place and route (overwrites hand edits)"
	@echo "make hardware-export                   Check and export review package"
	@echo "make hardware-check                    Check source invariants and calculations"
	@echo "make hardware-erc / hardware-drc        Run KiCad checks (requires KiCad 9)"
	@echo "make carrier-build                     Generate and route carrier (overwrites carrier hand edits)"
	@echo "make carrier-check / carrier-export     Check carrier / export portable review artifacts"
	@echo "make hardware-images                   Refresh schematic/PCB PNGs from current CAD; no regeneration"
	@echo "make hardware-review                   Export pad inventory and 1:1 mock-up PDFs; no CAD changes"
	@echo "make footprint-candidates              Prepare isolated corrections and native checks; saved CAD unchanged"
	@echo "make release-check BOARD=carrier       Report outstanding fabrication checks (fails until complete)"
	@echo "make release-check GATE=connection     Check fabrication and bench evidence before Pi connection"

.PHONY: hardware-review release-check footprint-candidates component-sync assembly-review

.PHONY: copper-screen
copper-screen:
	$(PYTHON) scripts/screen-interposer-copper.py

component-sync:
	/usr/bin/python3 scripts/sync-component-selections.py

assembly-review:
	/usr/bin/python3 scripts/export-assembly-review.py

footprint-candidates:
	/usr/bin/python3 scripts/prepare-footprint-candidates.py

hardware-review:
	/usr/bin/python3 scripts/export-hardware-review.py
	/usr/bin/python3 scripts/export-assembly-review.py

release-check:
	$(PYTHON) scripts/check-release.py --board "$(BOARD)" --gate "$(GATE)"

site-prepare:
	$(PYTHON) scripts/prepare-site.py

site-build: site-prepare
	$(HUGO) --source site --destination ../public --baseURL "$(BASE_URL)" --minify --cleanDestinationDir

site-serve: site-prepare
	$(HUGO) server --source site --port $(PORT) --baseURL "http://localhost:$(PORT)/" --disableFastRender

site-check: site-build
	$(PYTHON) scripts/check-site.py --base-url "$(BASE_URL)"

site-deploy:
	$(GH) workflow run pages.yml --repo "$(GITHUB_REPO)" --ref "$(DEPLOY_REF)"

.PHONY: hardware-generate hardware-build hardware-check hardware-erc hardware-drc hardware-export test

hardware-generate:
	$(PYTHON) scripts/generate-interposer.py

hardware-check:
	$(PYTHON) scripts/check-interposer.py

hardware-erc:
	$(PYTHON) scripts/check-interposer.py --kicad erc

hardware-drc:
	$(PYTHON) scripts/check-interposer.py --kicad drc

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

# Rebuild deliberately: this overwrites the generated design and manual edits.
hardware-build: hardware-generate
	/usr/bin/python3 scripts/layout-interposer.py
	/usr/bin/python3 scripts/route-interposer.py
	/usr/bin/python3 scripts/finalize-interposer.py

hardware-export: hardware-check hardware-erc hardware-drc
	$(PYTHON) scripts/export-interposer.py

.PHONY: carrier-generate carrier-build carrier-check carrier-erc carrier-drc carrier-export

carrier-generate:
	/usr/bin/python3 scripts/generate-carrier.py

carrier-build: carrier-generate
	/usr/bin/python3 scripts/route-carrier.py

carrier-check:
	/usr/bin/python3 scripts/check-carrier.py

carrier-erc:
	/usr/bin/python3 scripts/check-carrier.py --kicad erc

carrier-drc:
	/usr/bin/python3 scripts/check-carrier.py --kicad drc

carrier-export: carrier-check carrier-erc carrier-drc
	/usr/bin/python3 scripts/export-carrier.py

.PHONY: hardware-images
hardware-images:
	$(PYTHON) scripts/render_hardware_images.py
