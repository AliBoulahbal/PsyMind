from __future__ import annotations
import hashlib, io, re
from dataclasses import dataclass
from pypdf import PdfReader
from docx import Document as DocxDocument
from app.rag.embeddings import embed_many

@dataclass
class Piece:
    page:int|None
    section:str|None
    text:str

def sha256_bytes(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def extract_pdf(data:bytes)->list[Piece]:
    reader=PdfReader(io.BytesIO(data)); out=[]
    for i,page in enumerate(reader.pages,1):
        text=(page.extract_text() or "").strip()
        if text: out.append(Piece(i,None,text))
    return out

def extract_docx(data:bytes)->list[Piece]:
    doc=DocxDocument(io.BytesIO(data)); out=[]; section=None; buf=[]
    def flush():
        nonlocal buf
        text="\n".join(buf).strip()
        if text: out.append(Piece(None,section,text))
        buf=[]
    for p in doc.paragraphs:
        t=p.text.strip()
        if not t: continue
        if p.style and p.style.name.lower().startswith("heading"):
            flush(); section=t
        else: buf.append(t)
    flush(); return out

def extract(data:bytes,mime:str,filename:str)->list[Piece]:
    name=filename.lower()
    if mime=="application/pdf" or name.endswith(".pdf"): return extract_pdf(data)
    if mime=="application/vnd.openxmlformats-officedocument.wordprocessingml.document" or name.endswith(".docx"): return extract_docx(data)
    if mime.startswith("text/") or name.endswith(".txt"):
        return [Piece(None,None,data.decode("utf-8",errors="replace"))]
    raise ValueError("Unsupported document type. Allowed: PDF, DOCX, TXT")

def chunk_text(text:str,target_words:int=220,overlap_words:int=40)->list[str]:
    words=re.findall(r"\S+",text)
    if not words:return []
    chunks=[]; start=0
    while start<len(words):
        end=min(len(words),start+target_words)
        chunks.append(" ".join(words[start:end]))
        if end==len(words):break
        start=max(start+1,end-overlap_words)
    return chunks

def prepare_chunks(pieces:list[Piece]):
    rows=[]
    for piece in pieces:
        for text in chunk_text(piece.text):
            rows.append({"page_number":piece.page,"section":piece.section,"content":text,
                         "source_hash":hashlib.sha256(text.encode()).hexdigest()})
    vectors=embed_many([x["content"] for x in rows]) if rows else []
    for row,vec in zip(rows,vectors): row["embedding"]=vec
    return rows
