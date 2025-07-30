import httpx
import io
import pdfplumber
import re
import traceback

async def download_and_parse_pdf(url: str) -> list[str]:
    print(f"Downloading PDF from URL: {url}")

    try:
        async with httpx.AsyncClient() as client:
            print(f"Sending GET request to {url}")
            response = await client.get(url)
            print(f"Status Code: {response.status_code}")
            response.raise_for_status()

        print("✅ PDF downloaded successfully")

        # Now handle PDF parsing
        pdf_bytes = io.BytesIO(response.content)
        chunks = []
        current_chunk = ""

        with pdfplumber.open(pdf_bytes) as pdf:
            print(f"📄 Number of pages: {len(pdf.pages)}")
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split("\n")
                for line in lines:
                    if re.match(r"^\d+(\.\d+)*\s", line):
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = line
                    else:
                        current_chunk += " " + line

        if current_chunk:
            chunks.append(current_chunk.strip())

        print(f"✅ Parsed {len(chunks)} chunks")
        return chunks

    except Exception as e:
        print("❌ Exception occurred while parsing PDF:")
        traceback.print_exc()
        raise e
