from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
def fit(im, cx, cy, w, h, zoom=1.0):
    # crop box of aspect w:h centred on (cx, cy) fractions, scaled by zoom (1 = full height)
    iw, ih = im.size; ch = ih / zoom; cw = ch * w / h
    if cw > iw: cw = iw; ch = cw * h / w
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw); y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h), Image.LANCZOS)
def pop(im, c=1.1, b=1.05, s=1.1): return ImageEnhance.Color(ImageEnhance.Brightness(ImageEnhance.Contrast(im).enhance(c)).enhance(b)).enhance(s)
def shade_left(im, width, a=235):
    g = Image.new('L', im.size, 0); ImageDraw.Draw(g).rectangle([0, 0, width, im.size[1]], fill=a); g = g.filter(ImageFilter.GaussianBlur(width * 0.25))
    im.paste((0, 0, 0, 255), (0, 0), g)

