.PHONY: install run test clean trap

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

test:
	python -m pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +

trap:
	python assets/create_trap_pdf.py
