# NTU CSIE DIP 2024 Group 15: Final Project - 3D Virtual Try-on App

This repository hosts the final project for NTU CSIE DIP 2024, Group 15. The project is a 3D Virtual Try-on App designed to provide an interactive and realistic virtual fitting experience.

[SEE DEMO HERE Until 2025/01/05](http://solitude6060.asuscomm.com:9992/)

## Prerequisites

- Ensure you have Docker installed and running on your system.
- You will need an RTX 4090 GPU to run this project efficiently.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/solitude6060/3d-Virtual-Try-On-App.git
   ```

2. Navigate into the project directory:
   ```bash
   cd 3d-Virtual-Try-On-App
   ```

3. Run the setup script:
   ```bash
   bash setup_3d_virtual_try_on_app.sh
   ```

## Usage

- After successful setup, the Gradio app will be available at:
  ```
  http://localhost:9113
  ```

- You can also test the already running instance at:
  ```
  http://solitude6060.asuscomm.com:9992/
  ```

## Troubleshooting

If you encounter issues:

1. Check the environments of the individual Docker containers to ensure they are properly set up.
2. The most common issue is with the TRELLIS environment. Refer to the [TRELLIS GitHub repository](https://github.com/Microsoft/TRELLIS) for detailed installation instructions.
3. There might be some issue. You can fix it by install [kaolin](https://kaolin.readthedocs.io/en/latest/notes/installation.html) 
4. After fixing the TRELLIS environment, rerun the API script inside the container:
   ```bash
   cd TRELLIS && bash run_api.sh
   ```

## Acknowledgments

This project integrates components from the following repositories:

- [CatVTON](https://github.com/Zheng-Chong/CatVTON): Used for virtual try-on functionalities. All program ownership, except for FastAPI-related changes, remains with the original authors.
- [TRELLIS](https://github.com/Microsoft/TRELLIS): Used for 3D modeling capabilities. All program ownership, except for FastAPI-related changes, remains with the original authors.

## Contact

For any inquiries or support, please contact:

- Chung-Yao Ma: [chungyao.ma@gmail.com](mailto:chungyao.ma@gmail.com)
