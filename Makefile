.PHONY: run test demo

run:
	python3 -m src

test: demo

demo:
	sh tests/scripts/stage2_params.sh
	sh tests/scripts/stage3_vfs.sh
	sh tests/scripts/stage4_basic.sh
	sh tests/scripts/stage5_chown.sh