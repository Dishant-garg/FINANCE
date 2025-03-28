import tabula
import pandas as pd

def extract_table_from_pdf(pdf_path, output_csv_path, pages='all'):
    """
    Extracts tabular data from a PDF and saves it to a CSV file.

    :param pdf_path: Path to the input PDF file.
    :param output_csv_path: Path to the output CSV file.
    :param pages: Pages to extract from the PDF. Default is 'all'.
    """
    try:
        tables = tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True, lattice=True)

        combined_df = pd.concat(tables, ignore_index=True)

        combined_df.to_csv(output_csv_path, index=False)
        print(f"Data successfully extracted and saved to {output_csv_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pdf_path = "example.pdf"  # Replace with your PDF file path
    output_csv_path = "output.csv"  # Replace with your desired CSV file path
    extract_table_from_pdf(pdf_path, output_csv_path)