# QrBrysh: Stylized Qr Code Generator

This is a fork of the original source code for the paper "***ArtCoder: An End-to-end Method for Generating Scanning-robust Stylized QR Codes***".

There has been many changes and improvements, including: 

 * A complete web interface to select images and change the training parameters
 * Optimizations (I don't recall the numbers exactly but it's at least a x2 speedup)
 * Automatic segmentation of the input data for minimal encoding size
 * Base Qr code generation
 * Qart code implementation so the base code fits the target image, using saliency and edge detection

## Demos

<div align=center><img src="https://github.com/lapinozz/QrBrush/blob/main/data/demos/page.png" width="500"></div>

<table>
  
<tr>
   <td align="center">Style&Content</td>
   <td align="center">Output</td> 
</tr>
 
<tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/texture1.1.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_84.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/boy.jpg" width="230" /></td> 
</tr>

<tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/s55v2.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_105.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/boy.jpg" width="230" /></td> 
</tr>
    
 <tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/s6.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_170.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/boy.jpg" width="230" /></td> 
</tr>
    
 <tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/paper-cut.jpg" width="180" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_290.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/ship.jpg" width="230" /></td> 
</tr>  
 
 <tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/s45.2.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_78.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/dog.jpg" width="230" /></td> 
</tr>
    
 <tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/redwave4.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_182.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/ca.jpg" width="230" /></td> 
</tr>
    
<tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/s6.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_375.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/ca.jpg" width="230" /></td> 
</tr>
    
<tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/texture1.1.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_66.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/brad.jpg" width="230" /></td> 
</tr>

<tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/picasso_selfport1907.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/brad.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/brad.jpg" width="230" /></td> 
</tr>

<tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/s41.2.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_131.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/man.jpg" width="230" /></td> 
</tr>
 
 <tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/texture1.1.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_68.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/man.jpg" width="230" /></td> 
</tr>

<tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/candy.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_147.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/love.jpg" width="230" /></td> 
</tr>
    
<tr>
 <td height="250" width="280" align="center"><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/style/candy.jpg" width="230" /></td>
 <td rowspan="2" align="center" width="550" height="550"><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/demos/output_295.jpg" width="500" /></td>
</tr>
<tr height="250">
  <td align="center" width="280"><div align=center><div align=center><img src="https://github.com/SwordHolderSH/ArtCoder/blob/main/content/panda.jpg" width="230" /></td> 
</tr>

</table>

## Dependencies
 
 * Linux or Windows
 * CPU or NVIDIA GPU + CUDA CuDNN
 * Python 3
 * Pytorch 1.7.0
 * Other Python libraries I forgot about but you'll find out as you try to run it

## Getting Started

### Installation

* Clone this repo:
```
    git clone https://github.com/SwordHolderSH/ArtCoder
    cd ArtCoder
```
* Install PyTorch and other dependencies.

### Quick Start
* Start the server
```
    python ./src/app/main.py
```

It will start a webserver you can visit at http://localhost:8056 (and a webserver at ws://localhost:8057)
