"""Сборка листка 3. --execute выполняет все ячейки и сохраняет результаты."""
from pathlib import Path
import argparse
import re
import textwrap
import nbformat as nbf

ROOT = Path(__file__).resolve().parent
TARGET = ROOT/'Практические_листок_3.ipynb'


def build():
    sections = re.split(r'(?m)(?=^## 3\.)', (ROOT/'theory.md').read_text(encoding='utf-8'))
    cells = [nbf.v4.new_markdown_cell(sections[0]), nbf.v4.new_code_cell(textwrap.dedent('''
        from pathlib import Path
        import re
        import matplotlib.pyplot as plt
        from IPython.display import display, HTML
        import models
        from checks import run_checks
        get_ipython().run_line_magic('matplotlib', 'inline')
        models.setup()
        Path('animations').mkdir(exist_ok=True)

        def show_animation(index):
            fig, animation, update = models.ANIMATORS[index]()
            html = animation.to_jshtml(fps=15, default_mode='once')
            # Текстовые значки управления доступны даже без внешнего шрифта.
            icons = {'play': '▶', 'pause': 'Ⅱ', 'step-backward': '◀|',
                     'step-forward': '|▶', 'fast-backward': '|◀',
                     'fast-forward': '▶|', 'backward': '◀', 'forward': '▶',
                     'minus': '−', 'plus': '+'}
            for icon, symbol in icons.items():
                html = html.replace(f'<i class="fa fa-{icon}"></i>', symbol)
            html = html.replace('<i class="fa fa-play fa-flip-horizontal"></i>', '◀')
            html = re.sub(r'<link[^>]*font-awesome[^>]*>', '', html)
            html = chr(10).join(line.rstrip() for line in html.splitlines())
            output = Path('animations')/f'3_{index+1}.html'
            output.write_text('<!doctype html><html lang="ru"><meta charset="utf-8">'
                              + '<title>Листок 3 — анимация</title><body>' + html + '</body></html>',
                              encoding='utf-8')
            # Диагностические кадры для проверки изображения.
            qa = Path('.qa'); qa.mkdir(exist_ok=True)
            for frame in [0, models.FRAMES//2, models.FRAMES-1]:
                update(frame)
                fig.savefig(qa/f'3_{index+1}_{frame}.png', dpi=110, bbox_inches='tight')
            plt.close(fig)
            display(HTML(html))
            print('Сохранено:', output)
        print('Модели загружены. Для управления используйте кнопки под анимацией.')
    ''').strip())]
    for index, section in enumerate(sections[1:]):
        cells.append(nbf.v4.new_markdown_cell(section))
        cells.append(nbf.v4.new_code_cell(f'figure = models.PLOTTERS[{index}]()\nplt.show()'))
        cells.append(nbf.v4.new_code_cell(f'show_animation({index})'))
    cells.append(nbf.v4.new_markdown_cell('## Проверка результатов\n\nПроверяем физические инварианты, формулы и независимость времени спуска.'))
    cells.append(nbf.v4.new_code_cell("for label, value in run_checks().items():\n    print(label, ':', value)"))
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata.update({'kernelspec': {'name': 'practice-sheet-3', 'display_name': 'Python (Листок 3)', 'language': 'python'},
                        'language_info': {'name': 'python', 'version': '3.13'}})
    return nb


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    notebook = build()
    if args.execute:
        from nbclient import NotebookClient
        def report(cell, cell_index, **_):
            if cell.cell_type == 'code': print(f'Cell {cell_index+1}/{len(notebook.cells)}', flush=True)
        try:
            NotebookClient(notebook, timeout=1200, kernel_name='practice-sheet-3',
                           resources={'metadata': {'path': str(ROOT)}}, on_cell_start=report).execute()
        finally: nbf.write(notebook, TARGET)
    else: nbf.write(notebook, TARGET)
    print(str(TARGET).encode('ascii', errors='backslashreplace').decode(), flush=True)
