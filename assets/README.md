# assets

- `logo.png` - MDfier brand mark, shown in the app header (scaled to ~56 px tall) and
  used as the source for the icon. If absent, the header falls back to a "MDfier" text
  wordmark.
- `icon.png` - square icon derived from `logo.png` (center-cropped).
- `app.ico` - multi-size Windows icon (16-256 px) derived from `logo.png` with Pillow;
  used for the window/taskbar (via `app.setWindowIcon`) and the exe (`build.spec` `icon=`).
  The build works without it.
- `DejaVuSans.ttf` - Unicode font used by the `.md -> .pdf` converter (`fpdf2`). Optional:
  if absent, the app falls back to a Windows system font (Arial). Bundling it makes the
  portable `.exe` render full Unicode on machines without a suitable system font.
- `ocr_models/<key>/*.onnx` - optional PP-OCR recognition models fetched by
  `download_models.py` for non-built-in OCR languages.

To regenerate the icon after changing `logo.png`:

```bash
python -c "from PIL import Image; im=Image.open('assets/logo.png').convert('RGBA'); w,h=im.size; s=min(w,h); c=im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)); c.save('assets/icon.png'); c.save('assets/app.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
```
