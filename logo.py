import numpy as np
from funcs import logoFunc

import matplotlib
from matplotlib import pyplot as plt
import PIL.Image
import colorcet

def background(xscale=3):
	return np.mean(makeLogo(xscale*10)[-1])

defaultRes=2048
def makeLogo(x=0, y=0, xscale=3, xres=defaultRes, yres=defaultRes):
	xs=np.linspace(-xscale+x, x+xscale, xres)
	ys=np.linspace(y-1, y+30, yres)
	xys=np.array(np.meshgrid(xs, ys))
	zs=logoFunc(xys)
	zs=np.flip(zs, axis=0)
	return (xs, ys, xys, zs)

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LightSource

logoBack=background()

defaultCmap=colorcet.m_rainbow_r

def getColors(z, cmap=None):
	if cmap is None:
		cmap=defaultCmap
	mz=np.array(z)
	mz[mz>logoBack]=logoBack
	mz-=np.min(mz)
	mz/=np.max(mz)
	
	cols=cmap(mz)
	#cols=np.zeros((z.shape[0], z.shape[1], 4))
	
	#cols[:,:,3]=np.exp(-mz)
	return cols

def plotLogo3D(res=defaultRes):
	(x, y, xy, z)=makeLogo(xres=res, yres=res)
	
	fig = plt.figure()
	ax = Axes3D(fig)
	ax.view_init(elev=90, azim=90)
	
	ax.plot_surface(*xy, z, facecolors=getColors(z))
	
	#ax.contour(x, y, z)
	return fig

def plotLogo(res=defaultRes):
	(x, y, xy, z)=makeLogo(xres=res, yres=res)
	del(xy)
	del(x)
	del(y)
	imgData=getColors(z)
	del(z)
	im=PIL.Image.fromarray(np.array(imgData*255, dtype=np.int8), "RGBA")
	return im

from plumbum import cli
class LogoPlotterCLI(cli.Application):
	res=cli.SwitchAttr(["r", "resolution"], int, default=defaultRes, help="A resolution of the image. Use the highest possible.")
	threeD=cli.Flag(["3d"], help="Plot 3d")
	
	def main(self):
		if not self.threeD:
			im=plotLogo(res=self.res)
			im.save("logo.png", format="png")
		else:
			fig=plotLogo3D(res=self.res)
			plt.show()
		
if __name__=="__main__":
	LogoPlotterCLI.run()
