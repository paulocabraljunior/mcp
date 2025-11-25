from weasyprint import HTML
import sys

try:
    HTML(string="<h1>Hello World</h1>").write_pdf("test.pdf")
    print("WeasyPrint works!")
except Exception as e:
    print(f"WeasyPrint failed: {e}")
    sys.exit(1)
