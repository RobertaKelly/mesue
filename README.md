![Logo](/mesue.png)

# MESUE - Plugin para la Evaluación de Sustentabilidad Urbana Espacial
Herramienta de Sistemas de Información Geográfica para QGIS para la Evaluación de Sustentabilidad Urbana Espacial. 

> Basado en la herramienta [SSAM](https://github.com/gmassei/SSAM) (Spatial Sustainability Assessment Model).

## Requisitos 
- QGIS 3.10.2 o superior

## Instalación
Descargue o clone el repositorio, luego comprima la carpeta y agregue a sus complementos de QGIS. El complemento se agregará a la "Barra de herramientas" de QGIS.

## Para desarrolladores
```
rm *.pyc
pyuic5 -o ui_geoSUIT.py geoSUIT.ui
pyrcc5 -o resources.py resources.qrc
```
