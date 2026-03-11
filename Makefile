.PHONY: test demo-article demo-x demo-topic

test:
	pytest -q tests/test_router.py tests/test_pipeline.py

demo-article:
	python3 src/cli.py "https://www.stcn.com/article/detail/3666565.html"

demo-x:
	python3 src/cli.py "https://x.com/jain_web3/status/2029428696646598883"

demo-topic:
	python3 src/cli.py "OpenClaw Layered Search"
