import os
import uuid
import logging
import numpy as np
from pathlib import Path

from paddleocr import DocImgOrientationClassification, PaddleOCR
from PIL import Image

from claim_processing_pipeline.schemas import ProcessedDoc

logger = logging.getLogger(__name__)


def _resize_if_needed(img: Image.Image, file_size_kb: float, max_size_kb: float = 500) -> Image.Image:
    """
    Resizes image if file size exceeds threshold to reduce memory usage.
    
    Args:
        img: PIL Image object
        file_size_kb: Original file size in KB
        max_size_kb: Maximum allowed file size in KB
        
    Returns:
        Resized image if needed, otherwise original image
    """
    if file_size_kb <= max_size_kb:
        return img
    
    original_size = img.size
    size_ratio = max_size_kb / file_size_kb
    resize_ratio = size_ratio ** 0.5
    
    new_size = (int(img.size[0] * resize_ratio), int(img.size[1] * resize_ratio))
    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
    logger.info(f"Resized image {original_size} -> {new_size} ({file_size_kb:.0f}KB -> ~{max_size_kb:.0f}KB)")
    
    return resized_img


def _detect_and_correct_orientation(img: Image.Image) -> Image.Image:
    """
    Detects image orientation and rotates to upright position if needed.
    
    Args:
        img: PIL Image object
        
    Returns:
        Rotated image if correction needed, otherwise original image
    """
    logger.debug("Detecting orientation...")
    img_np = np.array(img)
    
    cls_model = DocImgOrientationClassification(model_name="PP-LCNet_x1_0_doc_ori")
    result = cls_model.predict(img_np)
    angle = int(result[0]["label_names"][0])
    
    if angle != 0:
        upright = img.rotate(angle, expand=True)
        logger.info(f"Rotated image by {angle}°")
        return upright
    
    logger.debug("No rotation needed")
    return img


def _extract_text_from_image(filename: str) -> str:
    """
    Extracts text from image using OCR with preprocessing.
    
    Args:
        filename: Path to image file
        
    Returns:
        Extracted text content
    """
    # Check file size
    file_size_bytes = os.path.getsize(filename)
    file_size_kb = file_size_bytes / 1024
    logger.debug(f"Image file size: {file_size_kb:.1f} KB")
    
    # Load and preprocess image
    img = Image.open(filename).convert("RGB")
    img = _resize_if_needed(img, file_size_kb)
    img = _detect_and_correct_orientation(img)
    
    # Run OCR
    logger.info("Running OCR...")
    ocr = PaddleOCR(lang="la")
    ocr_result = ocr.predict(np.array(img))
    content = "\n".join(ocr_result[0]["rec_texts"])
    logger.info(f"Extracted {len(content)} chars from OCR")
    
    return content


async def process_documents(filenames: list[str]) -> list[ProcessedDoc]:
    """
    Processes documents by extracting text content from text files or images using OCR.
    
    For text files (.md, .txt), reads content directly.
    For images, performs preprocessing steps:
    - Resizes large images to reduce memory usage (if needed)
    - Detects and corrects orientation
    - Runs OCR to extract text
    
    Args:
        filenames: List of file paths to process
        
    Returns:
        List of processed documents with extracted text content
    """
    processed_docs = []
    logger.info(f"Processing {len(filenames)} document(s)")

    for idx, filename in enumerate(filenames, 1):
        logger.info(f"[{idx}/{len(filenames)}] Processing: {Path(filename).name}")
        file_ext = Path(filename).suffix.lower()

        try:
            if file_ext in [".md", ".txt"]:
                content = Path(filename).read_text(encoding="utf-8")
            else:
                content = _extract_text_from_image(filename)

        except Exception as e:
            logger.error(f"Failed to process {Path(filename).name}: {type(e).__name__}: {e}")
            content = f"[ERROR: Could not process document - {str(e)}]"
        
        processed_docs.append(
            ProcessedDoc(
                id=str(uuid.uuid4()),
                name=filename,
                text=content,
                file_ext=file_ext,
            )
        )
        logger.info(f"Completed {Path(filename).name}")

    logger.info(f"Document processing complete: {len(processed_docs)} documents processed")
    return processed_docs
