from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
import os
from datetime import datetime
from typing import Optional
from PIL import Image
from model.pipeline import CatVTONPipeline
from model.cloth_masker import AutoMasker
from diffusers.image_processor import VaeImageProcessor
from utils import resize_and_crop, resize_and_padding
from huggingface_hub import snapshot_download
import torch

app = FastAPI()

# Define output directory
upload_imgs_dir = "upload_images"
os.makedirs(upload_imgs_dir, exist_ok=True)

output_dir = '../imgs/3d_targets'
os.makedirs(output_dir, exist_ok=True)

class SwapRequest(BaseModel):
    person_image_path: str
    cloth_image_path: str
    cloth_type: str  # "upper", "lower", or "overall"
    mask_path: Optional[str] = None

def process_image(person_path, cloth_path, cloth_type, mask_path=None):
    # Load model on demand
    base_model_path = "booksforcharlie/stable-diffusion-inpainting"
    resume_path = "zhengchong/CatVTON"
    repo_path = snapshot_download(repo_id=resume_path)

    pipeline = CatVTONPipeline(
        base_ckpt=base_model_path,
        attn_ckpt=repo_path,
        attn_ckpt_version="mix",
        weight_dtype=torch.float32,
        use_tf32=True,
        device='cuda'
    )
    mask_processor = VaeImageProcessor(vae_scale_factor=8, do_normalize=False, do_binarize=True, do_convert_grayscale=True)
    automasker = AutoMasker(
        densepose_ckpt=os.path.join(repo_path, "DensePose"),
        schp_ckpt=os.path.join(repo_path, "SCHP"),
        device='cuda'
    )

    # Load images
    person_image = Image.open(person_path).convert("RGB")
    cloth_image = Image.open(cloth_path).convert("RGB")

    # Resize images
    person_image = resize_and_crop(person_image, (768, 1024))
    cloth_image = resize_and_padding(cloth_image, (768, 1024))

    # Process mask
    if mask_path:
        mask = Image.open(mask_path).convert("L")
    else:
        mask = automasker(person_image, cloth_type)['mask']
        test_mask_dir = "test_mask"
        os.makedirs(test_mask_dir, exist_ok=True)
        test_mask_path = os.path.join(test_mask_dir, f"mask_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        mask.save(test_mask_path)
    mask = mask_processor.blur(mask, blur_factor=9)

    # Generate result
    result_image = pipeline(
        image=person_image,
        condition_image=cloth_image,
        mask=mask,
        num_inference_steps=50,
        guidance_scale=2.5
    )[0]

    # Save result
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(output_dir, f"result_{timestamp}.png")
    result_image.save(output_path)
    result_path = os.path.join(os.path.basename(os.path.dirname(output_path)), os.path.basename(output_path))

    # Release resources
    del pipeline
    del automasker
    torch.cuda.empty_cache()

    return result_path

@app.post("/swap")
async def swap_clothes(
    person_image: UploadFile = File(...),
    cloth_image: UploadFile = File(...),
    cloth_type: str = Form(...),
    mask: Optional[UploadFile] = File(None)
):
    # Save uploaded files
    person_path = os.path.join(upload_imgs_dir, f"person_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
    cloth_path = os.path.join(upload_imgs_dir, f"cloth_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
    mask_path = None

    with open(person_path, "wb") as f:
        f.write(person_image.file.read())

    with open(cloth_path, "wb") as f:
        f.write(cloth_image.file.read())

    if mask:
        mask_path = os.path.join(upload_imgs_dir, f"mask_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        with open(mask_path, "wb") as f:
            f.write(mask.file.read())
        
        # 確保 mask 與 person 圖像大小一致
        person_image_pil = Image.open(person_path).convert("RGB")
        mask_image_pil = Image.open(mask_path).convert("L")
        
        # 調整 mask 的大小以匹配 person_image
        if mask_image_pil.size != person_image_pil.size:
            mask_image_resized = mask_image_pil.resize(person_image_pil.size, Image.LANCZOS)
            mask_image_resized.save(mask_path)

    # Process and generate result
    output_path = process_image(person_path, cloth_path, cloth_type, mask_path)

    return {"output_path": output_path}
