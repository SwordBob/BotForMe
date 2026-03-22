# PDF Split Skill

## Description
Split large PDF files into smaller parts by page count. Useful for handling large PDFs that are difficult to read or process as a single file.

## When to use
- When a user asks to split a PDF file into smaller parts
- When a PDF is too large to handle or read conveniently
- When specific page ranges need to be extracted from a PDF
- When chapters or sections need to be separated

## Requirements
- Python 3.6+
- PyPDF2 library (automatically installed if missing)

## How to use
1. The skill will automatically detect if PyPDF2 is installed
2. If not installed, it will install it using pip
3. User provides the PDF file path and optional page count per part (default: 30)
4. Skill splits the PDF and saves files to an output directory

## Files
- `split_pdf.py`: Main script for splitting PDFs
- `README.md`: User documentation
- `requirements.txt`: Python dependencies

## Examples
```bash
# Split a PDF into 30-page parts
python split_pdf.py "large_document.pdf"

# Split into 50-page parts
python split_pdf.py "large_document.pdf" 50

# Split specific page range (e.g., pages 1-100)
python split_pdf.py "large_document.pdf" --range 1-100
```

## Notes
- Uses PyPDF2 instead of qpdf for better compatibility
- Automatically validates generated PDF files
- Creates a file list with validation status
- Handles large files efficiently