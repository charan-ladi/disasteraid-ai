# System Architecture

                +----------------+
                | Upload Input   |
                +--------+-------+
                         |
      +------------------+-----------------+
      |                  |                 |
   Image              Audio            Video
      |                  |                 |
 PaddleOCR        Whisper.cpp      Frame Extractor
      |                  |                 |
      +------------------+-----------------+
                         |
                    Extracted Text
                         |
                    Prompt Builder
                         |
                 TinyLlama / Phi-3
                         |
                 Structured JSON
                         |
             SQLite + CSV + Dashboard
