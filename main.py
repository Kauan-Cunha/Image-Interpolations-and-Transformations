import argparse
import src

def command_transform(args):
    if args.angle is not None and args.scale is not None:
        raise ValueError('Não é permitido colocar o angulo e fator de escala simultaneamente.')
    elif args.angle is None and args.scale is None:
        raise ValueError('Coloque ao menos o valor de uma das transformações')

    # Convertendo a string digitada no terminal para o Enum
    interpolation_enum = src.Interpolation(args.interpolation)
    
    # Utilizando o Dicionário de Estratégias do src.py
    funcao_interpolacao = src.ESTRATEGIAS_INTERPOLACAO[interpolation_enum]
    image = src.ImageManager(args.input, funcao_interpolacao)

    # Se dimensão não foi passada (é uma lista de 2 itens ou None)
    dim = tuple(args.dimension) if args.dimension else (image.img.shape[0], image.img.shape[1])

    if args.angle:
        image.rotate(args.angle, dim)
    if args.scale:
        image.scale(args.scale, dim)

    if args.output:
        if args.output[-3:] not in {'png', 'jpg'}: 
            raise ValueError('Você deve especificar a extensão (.png ou .jpg).')
        image.save_image(args.output, transformed=True)
    else:
        prefix = 'rotated' if args.angle else 'scale'
        val = args.angle if args.angle else args.scale
        suffix = 'rad' if args.angle else 'X'
        default_out = f"{prefix}_{val}{suffix}_{args.interpolation}.jpg"
        image.save_image(default_out, transformed=True)

    if args.show:
        image.show_image(transformed=True)

def command_panorama(args):
    if args.output[-4:] not in {'.jpg', 'jpeg'}: 
        raise ValueError('As imagens devem estar no formato JPEG.')

    detector_enum = src.FeatureDetectorType(args.detector)

    print(f"Iniciando registro de imagens usando detector: {detector_enum.value.upper()}")
    manager = src.PanoramaManager(args.imagem1, args.imagem2)
    manager.create_panorama(detector_enum, args.threshold, args.output, args.show_matches)

    # salvar imagens
    manager.save_image(file_name=f'panorama_{args.imagem1}_{args.imagem2}_limiar_{args.threshold}.jpg', img_type='panorama')
    manager.save_image(file_name=f'match_lines_{args.imagem1}_{args.imagem2}_limiar_{args.threshold}.jpg', img_type='lines')

    # mostrar imagens
    if args.show_matches: 
        manager.show_image(img_type='lines')

def main():
    parser = argparse.ArgumentParser(description="Laboratório 4 de PDI - Transformações e Registro de Imagens")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    subparsers.required = True

    # --- Configuração do comando TRANSFORM ---
    parser_transform = subparsers.add_parser("transform", help="Aplica transformações geométricas")
    parser_transform.add_argument('-i', '--input', required=True, help="Imagem de entrada (ex: img.jpg)")
    parser_transform.add_argument('-o', '--output', help="Imagem de saída (ex: out.png)")
    parser_transform.add_argument('-a', '--angle', type=float, help="Ângulo de rotação em radianos")
    parser_transform.add_argument('-e', '--scale', type=float, help="Fator de escala")
    parser_transform.add_argument('-d', '--dimension', type=int, nargs=2, metavar=('LARGURA', 'ALTURA'), help="Dimensão da saída")
    parser_transform.add_argument('-m', '--interpolation', default='bilinear', choices=['cni', 'lagrange', 'bilinear', 'bicubic'], help="Método de interpolação")
    parser_transform.add_argument('-s', '--show', action='store_true', help="Exibir a imagem na tela")

    # --- Configuração do comando PANORAMA ---
    parser_panorama = subparsers.add_parser("panorama", help="Registra um par de imagens gerando um panorama")
    parser_panorama.add_argument('-i1', '--imagem1', required=True, help="Primeira imagem do par")
    parser_panorama.add_argument('-i2', '--imagem2', required=True, help="Segunda imagem do par")
    parser_panorama.add_argument('-o', '--output', default="panorama_out.jpg", help="Nome do arquivo de saída")
    parser_panorama.add_argument('-d', '--detector', default='sift', choices=['sift', 'orb'], help="Detector de características")
    parser_panorama.add_argument('-t', '--threshold', type=float, default=0.75, help="Limiar para filtrar as correspondências")
    parser_panorama.add_argument('-s', '--show-matches', action='store_true', help="Exibir visualização das correspondências")

    # Lê os argumentos digitados no terminal
    args = parser.parse_args()

    # Redireciona para a função correta baseada no comando digitado
    if args.command == "transform":
        command_transform(args)
    elif args.command == "panorama":
        command_panorama(args)

if __name__ == "__main__":
    main()