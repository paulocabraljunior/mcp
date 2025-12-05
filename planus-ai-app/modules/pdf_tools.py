from pypdf import PdfReader
import io

class PDFContractReader:
    @staticmethod
    def extract_text(file_obj) -> str:
        """
        Extracts text from a PDF file object.
        """
        try:
            # Create a PDF reader object
            # file_obj is a BytesIO-like object from Streamlit
            reader = PdfReader(file_obj)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
