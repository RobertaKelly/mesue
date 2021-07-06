Esta herramienta digital forma parte del catálogo de herramientas del Banco Interamericano de Desarrollo. Puedes conocer más sobre la iniciativa del BID en [code.iadb.org](https://code.iadb.org/en).


![Logo](/mesue.png)

# MESUE - Modelo de Evaluación de Sustentabilidad Urbana Espacial.
Herramienta de Sistemas de Información Geográfica QGIS para la Evaluación de Sustentabilidad Urbana Espacial. 

MESUE es un complemento QGIS para la evaluación de la sostenibilidad urbana en el entorno geográfico, utilizando criterios de ambiente construido, ambiente biofísico, movilidad urbana y dinámicas socio-espaciales. Los resultados de MESUE son geográficos. La herramienta es open-source y puede ser utilizada de forma libre por investigadores, técnicos, estudiantes, planificadores y ciudadanía en general. Más datos y documentos están disponibles en https://llactalab.ucuenca.edu.ec.  463  git cmp "editing..."

> Basado en la herramienta [SSAM](https://github.com/gmassei/SSAM) (Spatial Sustainability Assessment Model).

## Tabla de contenidos:

* [Descripción y contexto](#-MESUE-Modelo-de-Evaluación-de-Sustentabilidad-Urbana-Espacial.)
* [Badges o escudos ](#-Badges-e-escudos)
* [Requisitos](#-Requisitos)
* [Guía de instalación](#-Instalación)
* [Para desarrollandores](#-Para-desarrolladores)
* [Autores](#-Autores)
* [Contactos](#-Contactos)
* [Licencia](#-Licencia)


## Badges o escudos
<img src="https://cdn.icon-icons.com/icons2/2415/PNG/512/python_original_wordmark_logo_icon_146382.png" alt="Python"  width="100" height="100"/>


## Requisitos 
- QGIS 3.10.2 o superior

## Instalación
Descargue el complemento MESUE haciendo click [aquí](https://github.com/llactalab/mesue/raw/master/mesue.zip) luego agregue a sus complementos de QGIS. El complemento se agregará a la "Barra de herramientas" de QGIS con el siguiente logo: ![Logo mesue](/icon2.png)

Al abrir se nos presentará la siguiente pantalla donde se prodrá seleccionar los indicadores que se quieran evaluar.

![Logo](/pantallaMesue.png)

## Para desarrolladores
```
rm *.pyc
pyuic5 -o ui_geoSUIT.py geoSUIT.ui
pyrcc5 -o resources.py resources.qrc
```
## Autores 
Johnatan Astudillo (Desarrollo y programación)

## Contactos

LlactaLAB – Ciudades Sustentables es un Grupo de Investigación de la Universidad de Cuenca, parte del Departamento Interdisciplinario de Espacio y Población.

llactalab@ucuenca.edu.ec

## Licencia 

[GNU General Public License v3.0](https://github.com/llactalab/mesue/blob/master/LICENSE)
