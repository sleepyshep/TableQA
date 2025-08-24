import os
import uuid
from pdf2image import convert_from_path
import subprocess

latex_preamble = r"""
\documentclass[standalone]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath, amsthm, amssymb, graphicx, geometry, array}
\usepackage{booktabs, multirow,natbib,tabularx, multicol, bm}
\usepackage[UTF8]{ctex}
\pagenumbering{gobble}
\begin{document}
\begin{table}[htp]
\centering
\resizebox*{0.5\columnwidth}{!}{ 
"""
latex_end = r"}\end{table}\end{document}"

def render_tex_to_pdf(tex_path, output_pdf_path, timeout=20):
    """Render a LaTeX file to PDF with unique temporary files for parallel processing"""
    with open(tex_path, "r") as file:
        tex_content = file.read()
    
    full_tex_content = latex_preamble + tex_content + latex_end
    
    # Generate unique temporary filename using UUID
    temp_tex_filename = f"temp_{uuid.uuid4().hex}.tex"
    temp_tex_path = os.path.join(os.path.dirname(output_pdf_path), temp_tex_filename)
    
    with open(temp_tex_path, "w") as temp_file:
        temp_file.write(full_tex_content)
    
    try:
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-output-directory", os.path.dirname(output_pdf_path), temp_tex_path],
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',  # 注意编码改为 utf-8
            timeout=timeout
        )
        
        # Get the actual output PDF path from LaTeX compilation
        temp_pdf_path = temp_tex_path.replace(".tex", ".pdf")
        
        if os.path.exists(temp_pdf_path):
            os.rename(temp_pdf_path, output_pdf_path)
            # print(f"Successfully rendered {tex_path} to PDF at {output_pdf_path}.")
        else:
            print(f"Error: PDF not generated for {tex_path}. LaTeX output:\n{result.stdout}")
    except subprocess.TimeoutExpired:
        print(f"Timeout expired while rendering {tex_path}. Skipping this file.")
    except Exception as e:
        print(f"Unexpected error rendering {tex_path}: {str(e)}")
    finally:
        # Cleanup temporary files
        for ext in [".aux", ".log", ".out", ".tex"]:
            file_path = temp_tex_path.replace(".tex", ext)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Warning: Could not delete temporary file {file_path}: {str(e)}")

def convert_pdf_to_png(pdf_path, png_path, dpi=300):
    """Convert PDF to PNG with error handling"""
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        if images:
            images[0].save(png_path, "PNG")
            # print(f"Converted {pdf_path} to {png_path}")
        else:
            print(f"Error: No pages found in {pdf_path}")
    except Exception as e:
        print(f"Error converting {pdf_path} to PNG: {str(e)}")
        
import cv2
import numpy as np

def crop_table_image(image_path):
    # 读取图像 (灰度模式)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"无法读取图像: {image_path}")
    
    # 检查图像是否全白（没有表格）
    if np.max(img) == 255 and np.min(img) == 255:
        # 生成空白图像警告
        blank_img = np.ones((img.shape[0] + 20, img.shape[1] + 20), dtype=np.uint8) * 255
        cv2.imwrite(image_path, blank_img)
        print(f"警告: 图像全白，无表格内容: {image_path}")
        return
    
    # 找到非白色像素的位置（像素值 < 250）
    rows, cols = np.where(img < 250)
    
    if len(rows) == 0 or len(cols) == 0:
        # 处理全白图像
        blank_img = np.ones((img.shape[0] + 20, img.shape[1] + 20), dtype=np.uint8) * 255
        cv2.imwrite(image_path, blank_img)
        return
    
    # 计算裁剪边界
    top = np.min(rows)
    bottom = np.max(rows)
    left = np.min(cols)
    right = np.max(cols)
    
    # 执行裁剪
    cropped_img = img[top:bottom+1, left:right+1]
    
    # 添加10像素白色边框
    border_size = 10
    bordered_img = cv2.copyMakeBorder(
        cropped_img, 
        border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT, 
        value=255
    )
    
    # 保存结果覆盖原文件
    cv2.imwrite(image_path, bordered_img)
        
ROOT_DIR = "/home/yangxuzheng/Workplace/fastapi/images/"
def latex_to_image(latex):
    base_name = str(uuid.uuid4().hex)
    # Generate LaTeX file
    tex_path = os.path.join(ROOT_DIR, f"{base_name}.tex")
    with open(tex_path, "w") as f:
        f.write(latex)
    
    # Generate PDF
    pdf_path = os.path.join(ROOT_DIR, f"{base_name}.pdf")
    render_tex_to_pdf(tex_path, pdf_path)
    
    # Convert to PNG
    if os.path.exists(pdf_path):
        png_path = os.path.join(ROOT_DIR, f"{base_name}.png")
        convert_pdf_to_png(pdf_path, png_path)
        crop_table_image(png_path)
        
        try:
            os.remove(tex_path)
            os.remove(pdf_path)
        except Exception as e:
            print(f"Error deleting temporary files: {e}")
        
        return f"/images/{base_name}.png"
    return None

if __name__ == "__main__":
    latex_code = r'''
\begin{tabular}{@{}cccccccccc@{}} \toprule \multirow{3}{*}{\textbf{D$_1$}} & \multirow{3}{*}{\textbf{Model}} & \multirow{3}{*}{\textbf{Score}} & \multicolumn{6}{c}{\textbf{w/o SACP} \textbackslash{} \textbf{w/ SACP}} \\ \cline{4-9} & & & \multicolumn{3}{c}{$\mathbf{\alpha=0.05}$} & \multicolumn{3}{c}{$\mathbf{\alpha=0.1}$} \\ \cline{4-6} \cline{7-9} & & & \texttt{Coverage} & \texttt{Size ($\downarrow$)} & \texttt{SSCV ($\downarrow$)} & \texttt{Coverage} & \texttt{Size ($\downarrow$)} & \texttt{SSCV ($\downarrow$)} \\ \midrule \multirow{12}{*}{\rotatebox[origin=c]{90}{Indian Pines}} & \multirow{3}{*}{\textbf{1D-CNN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 3.68 \textbackslash{} 2.28 & 0.41 \textbackslash{} 0.28 & 0.90 \textbackslash{} 0.90 & 2.52 \textbackslash{} 1.75 & 0.51 \textbackslash{} 0.45 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.94 & 4.09 \textbackslash{} 2.29 & 0.54 \textbackslash{} 0.57 & 0.90 \textbackslash{} 0.90 & 2.54 \textbackslash{} 1.74 & 0.88 \textbackslash{} 0.30 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 6.68 \textbackslash{} 4.31 & 2.48 \textbackslash{} 1.83 & 0.90 \textbackslash{} 0.90 & 5.56 \textbackslash{} 3.02 & 4.84 \textbackslash{} 1.95 \\ \cline{2-9} & \multirow{3}{*}{\textbf{3D-CNN}} & \texttt{APS} & 0.94 \textbackslash{} 0.95 & 5.73 \textbackslash{} 3.27 & 0.47 \textbackslash{} 0.38 & 0.90 \textbackslash{} 0.90 & 2.85 \textbackslash{} 2.06 & 0.35 \textbackslash{} 0.34 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 4.12 \textbackslash{} 3.92 & 0.10 \textbackslash{} 0.21 & 0.90 \textbackslash{} 0.90 & 3.21 \textbackslash{} 2.38 & 0.11 \textbackslash{} 0.25 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 6.40 \textbackslash{} 5.44 & 0.98 \textbackslash{} 0.95 & 0.91 \textbackslash{} 0.90 & 4.97 \textbackslash{} 3.72 & 1.61 \textbackslash{} 1.51 \\ \cline{2-9} & \multirow{3}{*}{\textbf{HybridSN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 5.56 \textbackslash{} 4.83 & 0.20 \textbackslash{} 0.16 & 0.90 \textbackslash{} 0.90 & 3.28 \textbackslash{} 2.74 & 0.92 \textbackslash{} 0.15 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 7.34 \textbackslash{} 1.72 & 0.40 \textbackslash{} 0.96 & 0.90 \textbackslash{} 0.90 & 4.29 \textbackslash{} 3.95 & 0.98 \textbackslash{} 0.75 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 6.79 \textbackslash{} 6.07 & 0.19 \textbackslash{} 0.41 & 0.90 \textbackslash{} 0.90 & 4.03 \textbackslash{} 3.40 & 0.64 \textbackslash{} 0.61 \\ \cline{2-9} & \multirow{3}{*}{\textbf{SSTN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 2.81 \textbackslash{} 1.73 & 0.42 \textbackslash{} 0.18 & 0.90 \textbackslash{} 0.90 & 2.00 \textbackslash{} 1.38 & 0.41 \textbackslash{} 0.47 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 2.52 \textbackslash{} 1.62 & 0.29 \textbackslash{} 0.30 & 0.90 \textbackslash{} 0.90 & 1.87 \textbackslash{} 1.36 & 0.29 \textbackslash{} 0.34 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 6.98 \textbackslash{} 4.16 & 4.38 \textbackslash{} 1.74 & 0.90 \textbackslash{} 0.90 & 5.33 \textbackslash{} 3.25 & 6.35 \textbackslash{} 3.09 \\ \midrule \multirow{12}{*}{\rotatebox[origin=c]{90}{Pavia University}} & \multirow{3}{*}{\textbf{1D-CNN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 2.26 \textbackslash{} 1.92 & 0.39 \textbackslash{} 0.37 & 0.90 \textbackslash{} 0.90 & 1.65 \textbackslash{} 1.57 & 0.40 \textbackslash{} 0.27 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 2.00 \textbackslash{} 1.83 & 0.23 \textbackslash{} 0.31 & 0.90 \textbackslash{} 0.90 & 1.59 \textbackslash{} 1.54 & 0.40 \textbackslash{} 0.29 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 3.92 \textbackslash{} 3.99 & 1.77 \textbackslash{} 2.21 & 0.90 \textbackslash{} 0.90 & 3.44 \textbackslash{} 3.04 & 3.62 \textbackslash{} 2.68 \\ \cline{2-9} & \multirow{3}{*}{\textbf{3D-CNN}} & \texttt{APS} & 0.94 \textbackslash{} 0.95 & 2.77 \textbackslash{} 2.34 & 1.04 \textbackslash{} 0.69 & 0.89 \textbackslash{} 0.89 & 2.14 \textbackslash{} 1.79 & 0.94 \textbackslash{} 0.66 \\ & & \texttt{RAPS} & 0.94 \textbackslash{} 0.94 & 2.57 \textbackslash{} 2.28 & 0.41 \textbackslash{} 0.66 & 0.89 \textbackslash{} 0.89 & 2.04 \textbackslash{} 1.76 & 0.64 \textbackslash{} 0.56 \\ & & \texttt{SAPS} & 0.94 \textbackslash{} 0.94 & 4.80 \textbackslash{} 4.31 & 4.56 \textbackslash{} 3.85 & 0.89 \textbackslash{} 0.89 & 4.04 \textbackslash{} 3.32 & 6.56 \textbackslash{} 4.23 \\ \cline{2-9} & \multirow{3}{*}{\textbf{HybridSN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 4.70 \textbackslash{} 4.59 & 0.59 \textbackslash{} 3.58 & 0.90 \textbackslash{} 0.90 & 3.38 \textbackslash{} 3.01 & 2.39 \textbackslash{} 1.33 \\ & & \texttt{RAPS} & 0.94 \textbackslash{} 0.95 & 5.50 \textbackslash{} 5.36 & 0.47 \textbackslash{} 0.36 & 0.89 \textbackslash{} 0.90 & 3.70 \textbackslash{} 3.74 & 0.81 \textbackslash{} 0.07 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 5.57 \textbackslash{} 5.44 & 1.98 \textbackslash{} 2.35 & 0.90 \textbackslash{} 0.90 & 3.99 \textbackslash{} 3.71 & 3.33 \textbackslash{} 3.47 \\ \cline{2-9} & \multirow{3}{*}{\textbf{SSTN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 1.75 \textbackslash{} 1.24 & 0.22 \textbackslash{} 0.26 & 0.90 \textbackslash{} 0.90 & 1.39 \textbackslash{} 1.11 & 0.23 \textbackslash{} 0.29 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 1.60 \textbackslash{} 1.22 & 0.20 \textbackslash{} 0.20 & 0.90 \textbackslash{} 0.90 & 1.13 \textbackslash{} 1.10 & 0.13 \textbackslash{} 0.23 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 3.26 \textbackslash{} 2.24 & 2.07 \textbackslash{} 0.92 & 0.90 \textbackslash{} 0.90 & 2.75 \textbackslash{} 1.91 & 2.96 \textbackslash{} 1.64 \\ \midrule \multirow{12}{*}{\rotatebox[origin=c]{90}{Salinas}} & \multirow{3}{*}{\textbf{1D-CNN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 1.40 \textbackslash{} 1.20 & 0.15 \textbackslash{} 0.15 & 0.90 \textbackslash{} 0.90 & 1.20 \textbackslash{} 1.09 & 0.18 \textbackslash{} 0.25 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 1.37 \textbackslash{} 1.20 & 0.06 \textbackslash{} 0.20 & 0.90 \textbackslash{} 0.90 & 1.19 \textbackslash{} 1.07 & 0.23 \textbackslash{} 0.25 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 3.63 \textbackslash{} 1.71 & 1.20 \textbackslash{} 0.16 & 0.90 \textbackslash{} 0.90 & 2.97 \textbackslash{} 1.28 & 2.04 \textbackslash{} 0.16 \\ \cline{2-9} & \multirow{3}{*}{\textbf{3D-CNN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 1.48 \textbackslash{} 1.25 & 0.20 \textbackslash{} 0.19 & 0.90 \textbackslash{} 0.90 & 1.17 \textbackslash{} 1.08 & 0.12 \textbackslash{} 0.16 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 1.47 \textbackslash{} 1.24 & 0.13 \textbackslash{} 0.18 & 0.90 \textbackslash{} 0.90 & 1.15 \textbackslash{} 1.07 & 0.15 \textbackslash{} 0.17 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 2.94 \textbackslash{} 2.02 & 0.58 \textbackslash{} 0.28 & 0.90 \textbackslash{} 0.90 & 2.39 \textbackslash{} 1.29 & 1.07 \textbackslash{} 0.13 \\ \cline{2-9} & \multirow{3}{*}{\textbf{HybridSN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 1.37 \textbackslash{} 1.09 & 0.18 \textbackslash{} 0.07 & 0.90 \textbackslash{} 0.90 & 1.10 \textbackslash{} 1.03 & 0.18 \textbackslash{} 0.23 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 1.20 \textbackslash{} 1.07 & 0.12 \textbackslash{} 0.10 & 0.90 \textbackslash{} 0.90 & 1.06 \textbackslash{} 1.00 & 0.12 \textbackslash{} 0.31 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 1.90 \textbackslash{} 1.37 & 0.42 \textbackslash{} 0.33 & 0.90 \textbackslash{} 0.90 & 1.66 \textbackslash{} 1.18 & 0.69 \textbackslash{} 0.31 \\ \cline{2-9} & \multirow{3}{*}{\textbf{SSTN}} & \texttt{APS} & 0.95 \textbackslash{} 0.95 & 1.70 \textbackslash{} 1.29 & 0.21 \textbackslash{} 0.16 & 0.90 \textbackslash{} 0.90 & 1.37 \textbackslash{} 1.08 & 0.23 \textbackslash{} 0.10 \\ & & \texttt{RAPS} & 0.95 \textbackslash{} 0.95 & 1.60 \textbackslash{} 1.18 & 0.12 \textbackslash{} 0.14 & 0.90 \textbackslash{} 0.90 & 1.29 \textbackslash{} 1.06 & 0.10 \textbackslash{} 0.11 \\ & & \texttt{SAPS} & 0.95 \textbackslash{} 0.95 & 5.42 \textbackslash{} 2.65 & 3.58 \textbackslash{} 0.86 & 0.90 \textbackslash{} 0.90 & 3.91 \textbackslash{} 2.07 & 3.64 \textbackslash{} 1.26 \\ \bottomrule \\ \multicolumn{9}{c}{\textbf{Ground Truth Table Image}} \\ \\ \multicolumn{9}{c}{Figure 4: Ground truth example of complex table.} \end{tabular}'''
    image_path = latex_to_image(latex_code)
    print(image_path)