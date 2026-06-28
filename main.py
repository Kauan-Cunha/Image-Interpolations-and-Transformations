from typing import Annotated
import typer
import src

app = typer.Typer()

@app.command()
def transform(img: Annotated[str, typer.Option('-i', '--input', '--image', '--entrada')]
        ,output: Annotated[str, typer.Option('-o', '--output', '--saida')] = None
        ,angle : Annotated[float, typer.Option('-a', '--angle', '--angulo')] = None
        ,factor: Annotated[float, typer.Option('-e', '--scale', '--escala')] = None
        ,dim: Annotated[tuple[int, int], typer.Option('-d', '--dimension', '--height', '--dimensao')] = None
        ,interpolation: Annotated[src.Interpolation, typer.Option('-m', '--interpolation', '--interpolacao')] = src.Interpolation.bilinear
        ,show_flag: Annotated[bool, typer.Option('-s', '--show')] = False):

    if angle is not None and factor is not None:
        raise ValueError('NÃO é permitido colocar o angulo e fator de escala simultaneamente.')
    elif angle is None and factor is None:
        raise ValueError('Coloque ao menos o valor de uma das transformações')

    #instanciando ImageManager
    func_interpolacao = src.ESTRATEGIAS_INTERPOLACAO[interpolation]
    image = src.ImageManager(img, func_interpolacao, gray_scale=True)
    
    #se não expecifica a dimensão de saida, mantém a da imagem original
    if dim is None:
        dim = (image.img.shape[0], image.img.shape[1])

    #pega a imagem aplicada a transformação
    if angle:
        image.rotate(angle, dim)
    
    if factor:
        image.scale(factor, dim)

    #salva o output
    if output:
        if output[-3:] not in {'.png', '.jpg'}: raise ValueError('Você deve especificar a extensão (Opções: .png e .jpg).')
        image.save_image(output, transformed=True)
        
    else:
        image.save_image( f"{'rotated' if angle else 'scale'}_{angle if angle else factor}{'X' if factor else 'rad'}_{interpolation}.jpg", 
                         transformed=True)
            
    
    #mostra se a flag show foi chamada
    if show_flag:
        image.show_image(transformed=True)

@app.command()
def panorama(
    img1: Annotated[str, typer.Option('-i1', '--imagem1', help="Primeira imagem do par")],
    img2: Annotated[str, typer.Option('-i2', '--imagem2', help="Segunda imagem do par")],
    output: Annotated[str, typer.Option('-o', '--output', help="Nome do arquivo de saída")] = "panorama_out.jpg",
    detector: Annotated[src.FeatureDetectorType, typer.Option('-d', '--detector', help="Detector de características (sift ou orb)")] = src.FeatureDetectorType.sift,
    threshold: Annotated[float, typer.Option('-t', '--threshold', help="Limiar para filtrar as correspondências (Teste de Lowe)")] = 0.75,
    show_matches: Annotated[bool, typer.Option('-s', '--show-matches', help="Exibir visualização das correspondências")] = False
):
    """
    Tarefa 1.2: Registra um par de imagens gerando um panorama.
    """
    if output[-4:] not in {'.jpg', 'jpeg'}: 
        raise ValueError('As imagens devem estar no formato JPEG.')

    print(f"Iniciando registro de imagens usando detector: {detector.value.upper()}")
    manager = src.PanoramaManager(img1, img2)
    manager.create_panorama(detector, threshold, output, show_matches)

    #salvar imagens
    manager.save_image(file_name=f'panorama_{img1}_{img2}_limiar_{threshold}', img_type='panorama')
    manager.save_image(file_name=f'match_lines_{img1}_{img2}_limiar_{threshold}', img_type='lines')

    #mostrar imagens
    if show_matches: manager.show_image(img_type='lines')

if __name__ == "__main__":
    app()


if __name__ == "__main__":
    app()