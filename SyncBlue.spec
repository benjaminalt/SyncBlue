# -*- mode: python -*-

block_cipher = None


a = Analysis(['src\\win\\eu\\syncblue\\syncblue.py'],
             pathex=['src\\win\\eu\\syncblue', 'C:\\Users\\benjaminalt\\Desktop\\Projects\\SyncBlue'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SyncBlue',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='src\\win\\icon.ico')
