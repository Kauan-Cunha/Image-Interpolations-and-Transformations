import matplotlib.pyplot as plt
import numpy as np
import math
from enum import Enum
from typing import Callable
import cv2

class Interpolation(str, Enum):
    cni = 'cni' #closest neighbor interpolation
    lagrange = 'lagrange'
    bilinear = 'bilinear'
    bicubic = 'bicubic'

class FeatureDetectorType(str, Enum):
    sift = 'sift'
    orb = 'orb'

def cn_interpolation(img: np.ndarray, x: float, y: float) -> int:
    """
    Input: img [ORIGINAL IMAGE]
           x [ORIGINAL COORDENATE X]
           y [ORIGINAL COORDENATE Y]
    
    RETURN: the intensity value applied Closest Neighbor Interpolation
    """
    x_ = min(round(x), img.shape[0] - 1)
    y_ = min(round(y), img.shape[1] - 1)

    return img[x_, y_]

def bilinear_interpolation(img: np.ndarray, x: float, y: float) -> int:
    """
    Input: img [ORIGINAL IMAGE]
           x [ORIGINAL COORDENATE X]
           y [ORIGINAL COORDENATE Y]
    
    RETURN: the intensity value applied Bilinear Interpolation
    """
    x_ = math.floor(x)
    y_ = math.floor(y)

    x1 = min(x_ + 1, img.shape[0] - 1)
    y1 = min(y_ + 1, img.shape[1] - 1)

    dx = x - x_
    dy = y - y_

    topLeft = (1 - dx) * (1 - dy) * img[x_, y_]
    topRight = dx * (1 - dy) * img[x1, y_]
    bottomLeft = (1 - dx) * dy * img[x_, y1]
    bottomRight = dx * dy * img[x1, y1]

    value = topLeft + topRight + bottomLeft + bottomRight
    return int(np.clip(value, 0, 255))

def bicubic_interpolation(img: np.ndarray, x: float, y: float) -> int:
    """
    Input: img [ORIGINAL IMAGE]
           x [ORIGINAL COORDENATE X]
           y [ORIGINAL COORDENATE Y]
    
    RETURN: the intensity value applied Bicubic Interpolation
    """
    x_ = math.floor(x)
    y_ = math.floor(y)
    dx = x - x_
    dy = y - y_

    def p(t: float) -> float:
        return t if t > 0 else 0
    def r(s:float) -> float:
        return (1/6)*(p(s+2)**3 - 4*p(s+1)**3 + 6*p(s)**3 - 4*p(s-1)**3)
    
    result = 0
    for m in range(-1, 3):
        for n in range(-1, 3):
           x_m = min(x_ + m, img.shape[0] - 1)
           y_n = min(y_ + n, img.shape[0] - 1)
           result += img[x_m, y_n]*r(m-dx)*r(dy-n)

    return np.clip(result, 0 , 255)

def lagrange_interpolation(img: np.ndarray, x: float, y: float) -> int:
    """
    Input: img [ORIGINAL IMAGE]
           x [ORIGINAL COORDENATE X]
           y [ORIGINAL COORDENATE Y]
    
    RETURN: the intensity value applied Lagrange Polinomial Interpolation
    """
    x_ = math.floor(x)
    y_ = math.floor(y)
    
    x_1 = min(x_ + 1, img.shape[0] - 1)
    x_2 = min(x_ + 2, img.shape[0] - 1)
    
    dx = x - x_
    dy = y - y_

    def l(n:int):
        y_2 = 0 if y_ + n - 2 < 0 else min(y_ + n - 2, img.shape[1] - 1)
        x__1 = 0 if x_ - 1 < 0 else x_ - 1

        a = (1/6)*(-dx) * (dx - 1) * (dx - 2)* img[x__1, y_2]
        b = (1/2)*(dx + 1)*(dx - 1)*(dx - 2) * img[x_, y_2]
        c = (1/2)*(-dx)*(dx + 1)*(dx - 2)*img[x_1, y_2]
        d = (1/6)*dx*(dx+1)*(dx-1)*img[x_2, y_2] 

        return a + b + c + d
    

    term1 = (1/6) * -dy * (dy - 1) * (dy - 2) * l(1)
    term2 = (1/2) * (dy + 1) * (dy - 1) * (dy - 2) * l(2)
    term3 = (1/2) * -dy * (dy + 1) * (dy - 2) * l(3)
    term4 = (1/6) * dy * (dy + 1) * (dy - 1) * l(4)

    return int(np.clip(term1 + term2 + term3 + term4, 0, 255))

ESTRATEGIAS_INTERPOLACAO = {
    Interpolation.cni: cn_interpolation,
    Interpolation.lagrange: lagrange_interpolation,
    Interpolation.bilinear: bilinear_interpolation,
    Interpolation.bicubic: bicubic_interpolation
}

class ImageManager():
    def __init__(self, file_name: str, interpolation: Callable, gray_scale:bool = False):
        self.img = self._load_image(file_name)
        self.transformed_img = None
        if gray_scale: self._to_grayscale()
        self._to_uint8()
        self.interpolation_func = interpolation

    def _load_image(self, file_name: str) -> np.ndarray:
        file_path = 'imgs/' + file_name
        return plt.imread(file_path)
    
    def _to_grayscale(self):
        """
        Converte a imagem para escala de cinza.
        """
        # Já está em escala de cinza
        if self.img.ndim == 2:
            return

        # Remove canal alfa, se existir
        rgb = self.img[..., :3]

        self.img = (
            0.299 * rgb[..., 0] +
            0.587 * rgb[..., 1] +
            0.114 * rgb[..., 2]
        )

    def _to_uint8(self):
        self.img = np.clip(self.img, 0, 255).astype(np.uint8)

    def rotate(self, angle: float, dim : tuple) -> None:
        result = np.empty((dim[0], dim[1]))
        for i in range(dim[0]):
            for j in range(dim[1]):
                x = i * math.cos(2*np.pi - angle) - j * math.sin(2*np.pi - angle)
                y = i * math.sin(2*np.pi - angle)  + j * math.cos(2*np.pi - angle)

                #essa condicional garante que x e y são um pixel na imagem original
                if (0 <= x <= self.img.shape[0]) and (0 <= y <= self.img.shape[1]):
                    value = self.interpolation_func(self.img, x, y)
                    result[i, j] = value
                else:
                    result[i, j] = 0
        
        self.transformed_img = result

    def scale(self, factor : float, dim : tuple) -> None:
        result = np.empty((dim[0], dim[1]))
        for i in range(dim[0]):
            for j in range(dim[1]):
                x = i * (1/factor)
                y = j * (1/factor)

                #essa condicional garante que x e y são um pixel na imagem original
                if (0 <= x < self.img.shape[0]) and (0 <= y < self.img.shape[1]):
                    value = self.interpolation_func(self.img, x, y)
                    result[i, j] = value
                else:
                    result[i, j] = 0
        
        self.transformed_img = result
    
    def save_image(self, file_name:str, transformed = False):
        if transformed:
            plt.imsave('img_results/' + file_name, self.transformed_img, cmap = 'gray')
        else:
            plt.imsave('img_results/' + file_name, self.img, cmap = 'gray')
        
    
    def set_interpolation(self, new_interpolation: Callable):
        self.interpolation_fun = new_interpolation
    
    def show_image(self, transformed = False):
        if transformed:
            plt.imshow(self.transformed_img, cmap='gray')
        else:
            plt.imshow(self.img, cmap= 'gray')
        
        plt.show()

class PanoramaManager:
    def __init__(self, img_path_1: str, img_path_2: str):
        self.img1_color = cv2.imread(f'imgs/{img_path_1}')
        self.img2_color = cv2.imread(f'imgs/{img_path_2}')
        self.img1_gray = cv2.cvtColor(cv2.imread(f'imgs/{img_path_1}'), cv2.COLOR_BGR2GRAY)
        self.img2_gray = cv2.cvtColor(cv2.imread(f'imgs/{img_path_2}'), cv2.COLOR_BGR2GRAY)

        self.paronama = None
        self.matches_img = None
        
    def create_panorama(self, detector_type: FeatureDetectorType, threshold: float, output_name: str, show_matches: bool):
        if detector_type == FeatureDetectorType.sift:
            detector = cv2.SIFT_create()
            norm_type = cv2.NORM_L2
        else: 
            detector = cv2.ORB_create()
            norm_type = cv2.NORM_HAMMING

        kp1, des1 = detector.detectAndCompute(self.img1_gray, None)
        kp2, des2 = detector.detectAndCompute(self.img2_gray, None)

        #Computar distâncias (similaridades)
        matcher = cv2.BFMatcher(norm_type)
        raw_matches = matcher.knnMatch(des1, des2, k=2)

        #selecionar com limiar
        good_matches = []
        for m, n in raw_matches:
            if m.distance < threshold * n.distance:
                good_matches.append(m)

        # Desenhar retas entre pontos correspondentes
        self.matches_img = cv2.drawMatches(self.img1_color, kp1, self.img2_color, kp2, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        # RANSAC
        if len(good_matches) < 4:
            raise ValueError(f"Pontos insuficientes para calcular a homografia. Encontrados: {len(good_matches)}.")

        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        height_img1, width_img1 = self.img1_color.shape[:2]
        height_img2, width_img2 = self.img2_color.shape[:2]
        panorama_width = width_img1 + width_img2
        panorama_height = max(height_img1, height_img2)

        panorama = cv2.warpPerspective(self.img1_color, H, (panorama_width, panorama_height))
        
        panorama[0:height_img2, 0:width_img2] = self.img2_color

        self.paronama = panorama
    
    def save_image(self, file_name:str, img_type:str):
        if img_type == 'panorama':
            cv2.imwrite(f'img_results/{file_name}.jpg', self.paronama)
        elif img_type == 'lines':
            cv2.imwrite(f'img_results/{file_name}.jpg', self.matches_img)

    def show_image(self, img_type:str):
        if img_type == 'panorama':
            plt.imshow(cv2.cvtColor(self.paronama, cv2.COLOR_BGR2RGB))
        elif img_type == 'lines':
            plt.imshow(cv2.cvtColor(self.matches_img, cv2.COLOR_BGR2RGB))
        
        plt.show()