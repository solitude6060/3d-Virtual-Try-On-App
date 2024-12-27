import gradio as gr
import os
import requests
from PIL import Image
import numpy as np
# from gradio_3d import ModelViewer  # Import for GLB visualization

# API endpoints
''' # remote server api on student's server
TRY_ON_API_URL = "http://solitude6060.asuscomm.com:9200/swap"
GEN_3D_API_URL = "http://solitude6060.asuscomm.com:9100/process-image/"
'''
TRY_ON_API_URL = "http://localhost:9111/swap" 
GEN_3D_API_URL = "http://localhost:9112/process-image" 


# Helper functions
def call_try_on_api(person_image_path, cloth_image_path, cloth_type, mask_path=None):
    files = {
        "person_image": open(person_image_path, "rb"),
        "cloth_image": open(cloth_image_path, "rb"),
        "cloth_type": (None, cloth_type),
    }
    if mask_path:
        files["mask"] = open(mask_path, "rb")
    response = requests.post(TRY_ON_API_URL, files=files)
    if response.status_code == 200:
        print("try on result", response.json())
        output_path = response.json()["output_path"]
        output_path = os.path.join("../imgs/", output_path)
        return output_path
    else:
        return None

def call_3d_api(image_path, return_type):
    print("image_path", image_path)
    print("return_type", return_type)
    image_path = os.path.join(os.path.basename(os.path.dirname(image_path)), os.path.basename(image_path))
    data = {"image_path": image_path, "return_type": return_type}
    response = requests.post(GEN_3D_API_URL, json=data)
    if response.status_code == 200:
        print("3d result", response.json())
        output_path = response.json()["output_path"]
        output_path = os.path.join("../imgs/", output_path)
        return output_path
    else:
        return None

def generate_mask(person_image):
    mask = Image.new("L", person_image.size, 0)
    return mask

# Gradio app
def process_try_on_api(person_image, cloth_image, cloth_type, mask_drawn, mask_layer):
    person_image_path = "person_image_temp.jpg"
    cloth_image_path = "cloth_image_temp.jpg"

    person_image.save(person_image_path)
    cloth_image.save(cloth_image_path)

    mask_path = None
    if mask_drawn:
        '''
        mask = mask_layer
        mask_path = "mask_temp.png"
        # print(type(mask))
        # print(mask)
        im = Image.fromarray(mask['composite'])
        im.save(mask_path)
        # mask['composite'].save(mask_path)
        '''
        mask = mask_layer["composite"]
        mask_array = np.array(mask)
        
        # Ensure the mask is black background and white drawing
        mask_array = np.where(mask_array > 0, 0, 255).astype(np.uint8)
        mask = Image.fromarray(mask_array).convert("L")
        
        mask_path = "mask_temp.png"
        mask.save(mask_path)
        mask.save("mask_temp.jpg")
        

    try_on_result = call_try_on_api(person_image_path, cloth_image_path, cloth_type, mask_path)
    if try_on_result is None:
        return "Error in API 1"

    if not try_on_result.startswith("/tmp"):
        try_on_result = os.path.abspath(try_on_result)

    return try_on_result, try_on_result

def process_3d_api(try_on_result, return_type):
    print("try_on_result", try_on_result)
    print("return_type", return_type)
    model_result = call_3d_api(try_on_result, return_type)
    
    if not try_on_result or not os.path.exists(try_on_result):
        return "Invalid input for API 2"
    
    if model_result is None:
        return "Error in API 2"

    if not model_result.startswith("/tmp"):
        model_result = os.path.abspath(model_result)
        
    model_result = os.path.join(os.path.basename(os.path.dirname(model_result)), os.path.basename(model_result))
    model_result = os.path.join("../imgs/", model_result)
    print("model_result", model_result)
    
    if return_type == "glb":
        print("model_result", model_result)
        return model_result, None
    else: 
        print("model_result", model_result)
        return None, model_result

def toggle_mask_layer(is_checked):
    if is_checked:
        return [gr.update(visible=True), gr.update(visible=True)]
    else:
        return [gr.update(visible=False), gr.update(visible=False)]

def create_blank_canvas():
    return np.ones((512, 512, 3), dtype=np.uint8) * 255  # 512x512 的黑色畫布

def clear_canvas(img):
    if img == None:
        return gr.update(value=create_blank_canvas())
    else:
        return img

# Gradio Interface
with gr.Blocks(title="DIP Group 15") as demo:
    gr.Markdown("""# 3D Virtual Try-On App""")

    with gr.Row():
        with gr.Column():
            person_image = gr.Image(type="pil", label="Upload Person Image")
            mask_drawn = gr.Checkbox(label="Draw Mask on Image", value=False)
            mask_layer = gr.Sketchpad(label="Draw Mask", visible=False, 
                                      value=create_blank_canvas())
            clear_button = gr.Button("Initial Person Image", visible=False)
            clear_button.click(clear_canvas, inputs=[person_image], outputs=[mask_layer])
            
            cloth_image = gr.Image(type="pil", label="Upload Cloth Image")
            cloth_type = gr.Radio(["upper", "lower", "overall"], label="Cloth Type", value="upper")
            return_type = gr.Radio(["gaussian", "radiance_field", "mesh", "glb"],
                                   label="3D Model Type", value="gaussian")
            submit_api1_btn = gr.Button("Try It On")
            submit_api2_btn = gr.Button("Generate 3D Model")

        with gr.Column():
            output_2d = gr.Image(label="2D Try-On Result")
            output_3d = gr.Video(label="3D Model Result")
            output_glb = gr.Model3D(
                label="3D GLB Model Viewer",
                clear_color=[0.6, 0.6, 0.6, 0.6],  # White background
                display_mode="solid",
            )

    person_image.change(lambda img: img, inputs=[person_image], outputs=[mask_layer])
    mask_drawn.change(toggle_mask_layer, inputs=[mask_drawn], outputs=[mask_layer, clear_button])

    try_on_result = gr.State()

    submit_api1_btn.click(
        process_try_on_api,
        inputs=[person_image, cloth_image, cloth_type, mask_drawn, mask_layer],
        outputs=[output_2d, try_on_result]
    )

    def route_3d_output(output_glb, output_3d, type):
        if type == "glb":
            return [output_glb, None]
        else:
            return [None, output_3d]

    submit_api2_btn.click(
        fn=process_3d_api,
        inputs=[try_on_result, return_type],
        outputs=[output_glb, output_3d]
    ).then(
        fn=route_3d_output,
        inputs=[output_glb, output_3d, return_type],
        outputs=[output_glb, output_3d]
    )


demo.launch(server_name="0.0.0.0", server_port=9113, share=True, allowed_paths=["../imgs/3d_targets", "../imgs/3d_outputs"])

