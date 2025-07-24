# Importera bibliotek för att hantera PDF-filer och textjämförelse
import PyPDF2
from difflib import Differ

# Funktion för att extrahera text från en PDF-fil
def extract_text_from_pdf(pdf_path):
    try:
        # Öppna PDF-filen
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            # Loopa igenom varje sida och extrahera text
            for page in pdf_reader.pages:
                text += page.extract_text() or ""  # Lägg till text från varje sida
            return text
    except Exception as e:
        print(f"Fel vid läsning av PDF: {e}")
        return ""

# Funktion för att jämföra två textsträngar
def compare_texts(text1, text2):
    differ = Differ()
    # Dela upp texterna i rader och jämför
    diff = list(differ.compare(text1.splitlines(), text2.splitlines()))
    # Skriv ut skillnader
    for line in diff:
        if line.startswith('+ ') or line.startswith('- '):
            print(line)

# Huvudprogram
def main():
    # Be användaren ange sökvägar till två PDF-filer
    pdf1_path = input("Ange sökväg till första PDF-filen: ")
    pdf2_path = input("Ange sökväg till andra PDF-filen: ")

    # Extrahera text från båda PDF-filerna
    print("Extraherar text från PDF-filerna...")
    text1 = extract_text_from_pdf(pdf1_path)
    text2 = extract_text_from_pdf(pdf2_path)

    if not text1 or not text2:
        print("Kunde inte läsa en eller båda PDF-filerna. Kontrollera sökvägarna.")
        return

    # Jämför texterna och visa skillnader
    print("\nSkillnader mellan PDF-filerna:")
    compare_texts(text1, text2)

# Kör programmet
if __name__ == "__main__":
    main()
