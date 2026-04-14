.PHONY: test compile-example demo stats clean

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

compile-example:
	PYTHONPATH=src python3 -m lattice compile \
		--input examples/materials/raw \
		--output outputs/materials \
		--domain materials \
		--dataset-name Lattice-Materials-v0.1

demo:
	PYTHONPATH=src python3 -m lattice demo \
		--raw-output data/demo_raw/solid_state \
		--compiled-output data/demo_compiled/solid_state \
		--domain materials \
		--dataset-name Lattice-Materials-RealDemo \
		--query "solid state battery electrolyte" \
		--compound "lithium iron phosphate" \
		--compound "lithium cobalt oxide"

stats:
	PYTHONPATH=src python3 -m lattice stats --path outputs/materials

clean:
	rm -rf outputs
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
