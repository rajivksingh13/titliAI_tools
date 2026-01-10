# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Include the entire openapi_generator package with all subdirectories
datas = [
    ('openapi_generator', 'openapi_generator'),
]
binaries = []
hiddenimports = ['openapi_generator', 'openapi_generator.generator', 'openapi_generator.web_ui', 'openapi_generator.multi_operation', 'openapi_generator.pdf_word_export', 'openapi_generator.trial_manager', 'flask', 'jinja2', 'werkzeug', 'yaml', 'weasyprint', 'reportlab', 'docx', 'docx.shared', 'docx.enum.text', 'docx.enum.style', 'docx.oxml', 'docx.oxml.ns', 'docx.oxml.text.paragraph', 'docx.oxml.table', 'docx.text.paragraph', 'docx.text.run']
tmp_ret = collect_all('flask')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jinja2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
# Collect PDF/Word export libraries if available
try:
    tmp_ret = collect_all('weasyprint')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except:
    pass
try:
    tmp_ret = collect_all('reportlab')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except:
    pass
try:
    tmp_ret = collect_all('docx')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except:
    pass


a = Analysis(
    ['run_flask_ui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='openapi-gen-ui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
