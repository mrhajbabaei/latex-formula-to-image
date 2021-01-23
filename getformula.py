import os
import cv2
import glob
import argparse
import subprocess
import numpy as np
from pdf2image import convert_from_path
from PIL import Image


def main(args):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, 'formulas')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # help: https://stackoverflow.com/questions/8085520/generating-pdf-latex-with-python-script
    content = r'''\documentclass[x11names]{report}
    \usepackage{background}
    \definecolor{lightkhaki}{rgb}{0.94, 0.9, 0.55}
    \thispagestyle{empty}
    \renewcommand\fbox{\fcolorbox{lightkhaki}{lightkhaki}}
    \backgroundsetup{
        scale=1,
        angle=0,
        opacity=1,
        contents={\begin{tikzpicture}[remember picture,overlay]
                \path [left color = lightkhaki,middle color = lightkhaki, right color = lightkhaki] (current page.south west)rectangle (current page.north east);
        \end{tikzpicture}}
    }
    \begin{document}
        \centering
        \setlength{\fboxsep}{2em}
        \fbox{
            $\displaystyle %(formula)s$
        }	
    \end{document}
    '''

    args = parser.parse_args()
    formula_tex_file = os.path.join(output_dir, 'formula.tex')
    with open(formula_tex_file,'w') as f:
        f.write(content%args.__dict__)

    cmd = ['pdflatex', '-interaction', 'nonstopmode', formula_tex_file]
    proc = subprocess.Popen(cmd)
    proc.communicate()

    file_path = os.path.join(current_dir, 'formula.pdf')
    retcode = proc.returncode
    if not retcode == 0:
        os.unlink(file_path)
        raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 

    os.unlink(formula_tex_file)
    os.unlink(os.path.join(current_dir, 'formula.log'))
    os.unlink(os.path.join(current_dir, 'formula.aux'))

    pages = convert_from_path(file_path, 500)
    image_files_number = len(glob.glob1(output_dir, '*.png'))
    output_image_file = os.path.join(output_dir, f'formula-{image_files_number}.png')

    for page in pages:
        # help: https://stackoverflow.com/questions/15474628/crop-the-border-of-an-image-using-pil
        nonwhite_positions = [(x,y) for x in range(page.size[0]) for y in range(page.size[1]) if page.getdata()[x+y*page.size[0]] != (255,255,255)]
        rect = (min([x for x,y in nonwhite_positions]), min([y for x,y in nonwhite_positions]), max([x for x,y in nonwhite_positions]), max([y for x,y in nonwhite_positions]))
        page.crop(rect).save(output_image_file, 'PNG')

    os.remove(file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--formula', default='I = \int_0^h y^2\mathrm{d}A')
    args = parser.parse_args()
    main(args)