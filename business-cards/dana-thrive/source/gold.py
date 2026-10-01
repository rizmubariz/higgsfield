import numpy as np
from PIL import Image
B='/home/user/danathrive-websitee/app/public/assets/brand/'
def gold(src, dst, scale=1, fill_holes=True):
    im=Image.open(B+src).convert('RGBA')
    if scale!=1: im=im.resize((im.width*scale,im.height*scale),Image.LANCZOS)
    a=np.asarray(im).astype(np.float32)/255
    rgb,al=a[...,:3],a[...,3]
    mx,mn=rgb.max(-1),rgb.min(-1)
    sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    # knock out white separators/halos and grey shadow (neutral pixels)
    keep=np.clip((sat-0.12)/0.18,0,1)
    from scipy import ndimage
    removed=(al*(1-keep)>0.5)|(al<0.5)
    lab,n=ndimage.label(removed)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    enclosed=removed & ~np.isin(lab,list(border)) & (al>0.5)
    if not fill_holes: enclosed[:]=False
    enclosed=ndimage.binary_dilation(enclosed,iterations=4)&(al>0.5)
    keep=np.where(enclosed,1.0,keep)
    L0=(0.2126*rgb[...,0]+0.7152*rgb[...,1]+0.0722*rgb[...,2])
    good=(~enclosed)&(keep>0.95)&(al>0.9)
    _,(iy,ix)=ndimage.distance_transform_edt(~good,return_indices=True)
    Lfix=np.where(enclosed,ndimage.uniform_filter(L0[iy,ix],5),L0)
    al2=al*keep
    L=Lfix
    m=al2>0.5; lo,hi=np.percentile(L[m],2),np.percentile(L[m],98)
    t=np.clip((L-lo)/(hi-lo),0,1)**0.85
    stops=np.array([[0.0,(150,112,52)],[0.5,(205,168,96)],[1.0,(240,218,160)]],dtype=object)
    c0,c1,c2=[np.array(s[1],np.float32)/255 for s in stops]
    out=np.where(t[...,None]<0.5, c0+(c1-c0)*(t[...,None]/0.5), c1+(c2-c1)*((t[...,None]-0.5)/0.5))
    res=np.dstack([out,al2]); Image.fromarray((res*255).astype(np.uint8)).save(dst)
gold('logo-icon.png','assets/gold-icon.png',2)
gold('logo-wordmark.png','assets/gold-wordmark.png',2,fill_holes=False)
