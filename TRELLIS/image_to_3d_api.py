import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
from trellis.pipelines import TrellisImageTo3DPipeline
from trellis.utils import render_utils, postprocessing_utils
import imageio

# 環境設定
os.environ['SPCONV_ALGO'] = 'native'

# 儲存位置
save_dir = '../imgs/3d_outputs'

# 初始化 FastAPI 應用
app = FastAPI()

# 加載模型
pipeline = TrellisImageTo3DPipeline.from_pretrained("JeffreyXiang/TRELLIS-image-large")
pipeline.cuda()

# 請求模型
class ImageRequest(BaseModel):
    image_path: str  # 相片位置
    return_type: str  # 'gaussian', 'radiance_field', 'mesh', or 'glb'

@app.post("/process-image/")
async def process_image(request: ImageRequest):
    image_path = request.image_path
    # 確認檔案是否存在
    if not os.path.exists(image_path):
        print('check in imgs folder')
        image_path = os.path.join('../imgs/', image_path)
        print('new image_path', image_path)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found")

    try:
        # 加載影像
        image = Image.open(image_path)

        # 執行處理流水線
        outputs = pipeline.run(image, seed=1)

        if request.return_type == 'gaussian':
            video = render_utils.render_video(outputs['gaussian'][0])['color']
            video_path = "gaussian.mp4"
            video_path = os.path.join(save_dir, video_path)
            imageio.mimsave(video_path, video, fps=30)
            output_path = os.path.join(os.path.basename(os.path.dirname(video_path)), os.path.basename(video_path))
            return {"file_path": output_path}

        elif request.return_type == 'radiance_field':
            video = render_utils.render_video(outputs['radiance_field'][0])['color']
            video_path = "radiance_field.mp4"
            video_path = os.path.join(save_dir, video_path)
            imageio.mimsave(video_path, video, fps=30)
            output_path = os.path.join(os.path.basename(os.path.dirname(video_path)), os.path.basename(video_path))
            return {"file_path": output_path}

        elif request.return_type == 'mesh':
            video = render_utils.render_video(outputs['mesh'][0])['normal']
            video_path = "mesh.mp4"
            video_path = os.path.join(save_dir, video_path)
            imageio.mimsave(video_path, video, fps=30)
            output_path = os.path.join(os.path.basename(os.path.dirname(video_path)), os.path.basename(video_path))
            return {"file_path": output_path}

        elif request.return_type == 'glb':
            glb = postprocessing_utils.to_glb(
                outputs['gaussian'][0],
                outputs['mesh'][0],
                simplify=0.95,
                texture_size=1024,
            )
            glb_path = "output.glb"
            glb_path = os.path.join(save_dir, glb_path)
            glb.export(glb_path)
            output_path = os.path.join(os.path.basename(os.path.dirname(glb_path)), os.path.basename(glb_path))
            return {"file_path": output_path}
        else:
            raise HTTPException(status_code=400, detail="Invalid return_type")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 啟動伺服器時，執行 `uvicorn <filename>:app --reload`
