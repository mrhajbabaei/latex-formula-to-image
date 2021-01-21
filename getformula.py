import os
import glob
import argparse
import subprocess
from pdf2image import convert_from_path
from PIL import Image


def main(args):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, 'formulas')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # help: https://stackoverflow.com/questions/8085520/generating-pdf-latex-with-python-script
    content = r'''\documentclass{standalone}
    \usepackage{xcolor}
    \definecolor{khaki}{rgb}{0.94, 0.9, 0.55}
    \begin{document}
    \colorbox{khaki}{$\displaystyle %(formula)s$}
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
        width, height = page.size
        page.crop((5, 5, width-5, height-5)).save(output_image_file, 'PNG')

    os.remove(file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--formula', default='I = \int_0^h y^2\mathrm{d}A')
    args = parser.parse_args()
    main(args)